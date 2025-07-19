import pyodbc
import numpy as np
import pandas as pd
import time
import re
from sentence_transformers import SentenceTransformer
import faiss


# --- Configuration ---
SERVER = ''
DATABASE = ''
USERNAME = ''
PASSWORD = ''
INPUT_TABLE = ''
OUTPUT_TABLE = ''
KEY_ATTRIBUTES = ['']
GROUP_ID_COLUMN = 'GroupID'
UNIQUE_FLAG_COLUMN = 'IsUnique'
MATCH_SCORE_COLUMN = 'MatchScore'
GROUP_BY_COLUMNS = ['', '']
SIMILARITY_THRESHOLD = 0.85
BATCH_SIZE = 1000

# --- Stopword List ---
STOPWORDS = set("""
the and of in for on at to with by from or as is are was were be this that & llc l.l.c a about above after again against all am an any are as at be because been before being below between both but by
could did do does doing down during each few for from further had has have having he her here hers herself him himself
his how i if in into is it its itself me more most my myself no nor not of off on once only or other ought our ours
ourselves out over own same she should so some such than that the their theirs them themselves then there these they
this those through to too under until up very was we were what when where which while who whom why with would you
your yours yourself yourselves company pjsc p.j.s.c incorporated inc ltd limited
""".split())

# --- Database Connection ---
conn_str = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};'
)
cnxn = pyodbc.connect(conn_str)
cursor = cnxn.cursor()
print("✅ Connected to SQL Server.")

# --- Preprocessing ---
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = text.split()
    return ' '.join([t for t in tokens if t not in STOPWORDS])

# --- Fetch Data ---
def fetch_data(table_name, columns):
    df = pd.read_sql(f"SELECT * FROM {table_name}", cnxn)
    df['__combined__'] = df[columns].astype(str).agg(' '.join, axis=1)
    df['__combined__'] = df['__combined__'].apply(preprocess_text)
    return df

# --- Embedding ---
def embed_records(texts, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

# --- FAISS Nearest Neighbor Grouping ---
def find_neighbors_faiss_with_scores(vectors, similarity_threshold=0.85):
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(vectors)
    similarities, indices = index.search(vectors, k=10)

    assigned = [-1] * len(vectors)
    match_scores = [0.0] * len(vectors)
    group_id = 1

    for i in range(len(vectors)):
        if assigned[i] != -1:
            continue
        assigned[i] = group_id
        max_score = 0
        for j, sim in zip(indices[i], similarities[i]):
            if i != j and sim >= similarity_threshold and assigned[j] == -1:
                assigned[j] = group_id
                if sim > max_score:
                    max_score = sim
        match_scores[i] = round(max_score * 100, 2)
        group_id += 1

    return assigned, match_scores

# --- SQL Writer with fast_executemany + batch insert ---
def write_results_to_table(df, group_ids, match_scores, table_name, batch_size=1000):
    df = df.copy()
    df[GROUP_ID_COLUMN] = group_ids
    df[MATCH_SCORE_COLUMN] = match_scores
    df[UNIQUE_FLAG_COLUMN] = df.groupby(GROUP_ID_COLUMN)[GROUP_ID_COLUMN].transform('count') == 1
    df[UNIQUE_FLAG_COLUMN] = df[UNIQUE_FLAG_COLUMN].astype(int)

    # Create table if doesn't exist
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
    if not cursor.fetchall():
        col_defs = ', '.join([f"[{col}] VARCHAR(MAX)" for col in df.columns if col not in [GROUP_ID_COLUMN, MATCH_SCORE_COLUMN, UNIQUE_FLAG_COLUMN]])
        create_query = (
            f"CREATE TABLE {table_name} ({col_defs}, "
            f"{GROUP_ID_COLUMN} INT, {MATCH_SCORE_COLUMN} FLOAT, {UNIQUE_FLAG_COLUMN} BIT)"
        )
        cursor.execute(create_query)
        cnxn.commit()

    # Clear existing data
    cursor.execute(f"DELETE FROM {table_name}")
    cnxn.commit()

    # Prepare fast insertion
    insert_cols = df.columns.tolist()
    insert_query = f"INSERT INTO {table_name} ({', '.join(insert_cols)}) VALUES ({', '.join(['?'] * len(insert_cols))})"
    records = [
        [str(row[col]) if col not in [GROUP_ID_COLUMN, MATCH_SCORE_COLUMN, UNIQUE_FLAG_COLUMN]
         else float(row[col]) if col == MATCH_SCORE_COLUMN
         else int(row[col]) for col in insert_cols]
        for _, row in df.iterrows()
    ]

    fast_cursor = cnxn.cursor()
    fast_cursor.fast_executemany = True

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        fast_cursor.executemany(insert_query, batch)
        cnxn.commit()

    print(f"✅ Inserted {len(df)} rows to '{table_name}'.")

# --- Main Execution ---
if __name__ == "__main__":
    start_time = time.time()

    print("📥 Loading data...")
    df = fetch_data(INPUT_TABLE, KEY_ATTRIBUTES)

    print("🔍 Grouping by BU_GROUP + COUNTRY...")
    all_results = []
    current_group_id = 1

    for group_keys, group_df in df.groupby(GROUP_BY_COLUMNS):
        if group_df.empty:
            continue
        print(f"➡️ Processing group: {group_keys} ({len(group_df)} records)")

        embeddings = embed_records(group_df['__combined__'].tolist())
        local_group_ids, match_scores = find_neighbors_faiss_with_scores(embeddings, SIMILARITY_THRESHOLD)

        # Adjust group IDs
        gid_map = {}
        adjusted_ids = []
        for gid in local_group_ids:
            if gid == -1:
                adjusted_ids.append(-1)
            else:
                if gid not in gid_map:
                    gid_map[gid] = current_group_id
                    current_group_id += 1
                adjusted_ids.append(gid_map[gid])

        group_df = group_df.drop(columns=['__combined__'])
        group_df[GROUP_ID_COLUMN] = adjusted_ids
        group_df[MATCH_SCORE_COLUMN] = match_scores
        all_results.append(group_df)

    print("📦 Combining all results...")
    final_df = pd.concat(all_results, ignore_index=True)

    print("📤 Writing to SQL (fast mode)...")
    write_results_to_table(final_df, final_df[GROUP_ID_COLUMN], final_df[MATCH_SCORE_COLUMN], OUTPUT_TABLE, batch_size=BATCH_SIZE)

    cursor.close()
    cnxn.close()

    print(f"✅ Done. ⏱️ Total time: {time.time() - start_time:.2f} seconds.")


