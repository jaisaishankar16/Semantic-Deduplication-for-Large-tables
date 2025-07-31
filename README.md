Here is the README.md file in GitHub markdown format:

**Semantic Deduplication System**
============================

**Problem Statement**
-------------------

This project aims to develop a semantic deduplication system that groups similar records in a database based on their semantic similarity. The system uses natural language processing techniques to embed records into vector spaces and then uses a nearest neighbor search algorithm to group similar records together.

**Dependencies and Requirements**
------------------------------

* Python 3.7 or higher
* ODBC Driver 17 for SQL Server
* pyodbc library
* pandas library
* numpy library
* sentence-transformers library
* faiss library
* SQL Server database with the necessary tables and columns

**Project Structure**
-------------------

The project consists of the following files and folders:
* `Semantic_Dedup.py`: The main script that runs the deduplication process
* `stopwords.txt`: The stopword list used for preprocessing text data
* `config.ini`: The configuration file that contains the database connection details and other settings
* `requirements.txt`: The file that lists the required libraries and their versions

**How to Run**
--------------

1. Install the required libraries by running `pip install -r requirements.txt`
2. Create a copy of the `config.ini` file and fill in the necessary details (e.g. database connection details, table names)
3. Run the `Semantic_Dedup.py` script using `python Semantic_Dedup.py`
4. The script will output the results to the specified output table in the SQL Server database

**Ideology and Solution**
-------------------------

The system uses a combination of natural language processing techniques and nearest neighbor search algorithms to group similar records together. The preprocessing step involves tokenizing text data, removing stop words, and embedding the text data into vector spaces using a sentence transformer model. The FAISS nearest neighbor search algorithm is then used to find the most similar records in the vector space. The system assigns a group ID to each record based on its similarity score and writes the results to the output table in the SQL Server database.

**Technologies Used**
---------------------

* Python 3.7
* ODBC Driver 17 for SQL Server
* pyodbc library
* pandas library
* numpy library
* sentence-transformers library
* faiss library
* SQL Server database

**Contact Info**
--------------

For any queries, reach out to konashankar097@gmail.com