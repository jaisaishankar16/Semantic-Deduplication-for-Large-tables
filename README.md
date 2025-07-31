# Semantic_Dedup
## Problem Statement
This project is designed to solve the problem of deduplicating semantically similar records in a SQL database. It uses a combination of natural language processing techniques, including sentence embedding and FAISS (Facebook AI Similarity Search) to group similar records together.

## Dependencies and Requirements
* Python 3.8+
* pyodbc (ODBC driver for SQL Server)
* numpy
* pandas
* sentence_transformers
* faiss
* ODBC Driver 17 for SQL Server

## Project Structure
The project consists of the following major files and folders:
* `Semantic_Dedup.py`: The main script that contains the implementation of the deduplication algorithm.
* `config.py`: A configuration file that contains the database connection details and other project settings.
* `stopwords.txt`: A file containing a list of stop words used for preprocessing.
* `models`: A folder containing pre-trained sentence embeddings models.

## How to Run
To run the project, follow these steps:
1. Install the required dependencies using pip: `pip install pyodbc numpy pandas sentence-transformers faiss`
2. Create a configuration file `config.py` with the following format:
```python
SERVER = 'your_server_name'
DATABASE = 'your_database_name'
USERNAME = 'your_username'
PASSWORD = 'your_password'
INPUT_TABLE = 'your_input_table_name'
OUTPUT_TABLE = 'your_output_table_name'
KEY_ATTRIBUTES = ['your_attribute1', 'your_attribute2']
GROUP_ID_COLUMN = 'GroupID'
UNIQUE_FLAG_COLUMN = 'IsUnique'
MATCH_SCORE_COLUMN = 'MatchScore'
GROUP_BY_COLUMNS = ['your_column1', 'your_column2']
SIMILARITY_THRESHOLD = 0.85
BATCH_SIZE = 1000
```
3. Run the main script `Semantic_Dedup.py` using Python: `python Semantic_Dedup.py`

## Ideology and Solution
The project uses a combination of natural language processing techniques to deduplicate semantically similar records in a SQL database. The main steps are:
1. Preprocessing: The input data is preprocessed by converting all text to lowercase and removing stop words.
2. Sentence Embedding: The preprocessed text is then embedded using a sentence embedding model.
3. FAISS Nearest Neighbor Grouping: The embedded vectors are then used to find the nearest neighbors using the FAISS algorithm.
4. Grouping: The nearest neighbors are then grouped together based on the similarity threshold.
5. Writing to SQL: The grouped records are then written to the output table in the SQL database.

## Technologies Used
* Python
* pyodbc (ODBC driver for SQL Server)
* numpy
* pandas
* sentence-transformers
* faiss
* ODBC Driver 17 for SQL Server

## Contact
For any queries, reach out to konashankar097@gmail.com