import mysql.connector
import pandas as pd
import numpy as np
import json
import sys
import os
import dotenv
from find_papers_by_keyword.utils import gen_sql_in_tup
from find_papers_by_keyword.embeddings_generator import EmbeddingsGenerator

inFile = sys.argv[1]


def _get_abstract_from_IA(index_length, inverted_index):
    token_list = [None] * index_length
    for token in inverted_index:
        for ind in inverted_index[token]:
            token_list[ind] = token
    token_list = list(filter(None, token_list))
    abstract = u' '.join(token_list)
    return abstract

def convert(row):
        indexed_abstract = row['IndexedAbstract']
        index_json = json.loads(indexed_abstract)
        index_length = index_json['IndexLength']
        inverted_index = index_json['InvertedIndex']

        return  _get_abstract_from_IA(index_length, inverted_index)

dotenv.load_dotenv()

db = mysql.connector.connect(
    user=os.getenv('MYSQL_USER'), 
    password=os.getenv('MYSQL_PASS'), 
    host="mag-2020-09-14.mysql.database.azure.com", 
    port=3306, 
    database=os.getenv('MYSQL_DB'), 
    ssl_ca="DigiCertGlobalRootCA.crt.pem", 
    ssl_disabled=False
)

nrows = 10**4
chunksize = 4 
iters = nrows / chunksize

get_papers_by_id_sql = "SELECT * FROM Papers WHERE PaperId IN (%s)"

reader = pd.read_csv(inFile, sep='\t', names=['id', 'IndexedAbstract'], chunksize=4)
for i, df in enumerate(reader):
    converted_df = pd.concat([df['id'], df.apply(convert, axis=1)], axis=1, keys=['id', 'Abstract'])
    
    ids = tuple(df['id'])
    fields_in_sql = gen_sql_in_tup(len(ids))
    get_papers_by_id_sql = f"SELECT PaperId as id, PaperTitle as title FROM Papers WHERE PaperId IN {fields_in_sql};"

    with db.cursor(dictionary=True) as dict_cur:
        dict_cur.execute(get_papers_by_id_sql, ids)
        papers = dict_cur.fetchall()

    for paper in papers:
        paper['abstract'] = (converted_df[converted_df['id'] == paper['id']])['Abstract'].values[0]

    generator = EmbeddingsGenerator()
    embeddings = generator.generate_paper_embeddings(papers)
    print(embeddings)
    if i >= 5:
        break