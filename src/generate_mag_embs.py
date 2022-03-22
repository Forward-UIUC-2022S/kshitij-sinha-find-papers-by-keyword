import mysql.connector
import pandas as pd
import numpy as np
import json
import sys
import os
import dotenv
from find_papers_by_keyword.utils import gen_sql_in_tup
from find_papers_by_keyword.embeddings_generator import EmbeddingsGenerator
import pickle
from memory_profiler import profile, memory_usage
import time

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

def generate_embeddings_and_save(batch, generator, embs_file, id_to_ind_file):
    embs, id_to_ind = generator.generate_paper_embeddings(batch)
    pickle.dump(embs, embs_file)
    pickle.dump(id_to_ind, id_to_ind_file)

@profile
def main():
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

    limit = 10**7
    get_papers_sql = f"""
        SELECT papers.PaperId AS id, papers.PaperTitle AS title, paperabstracts.Abstract AS abstract
        FROM papers
        JOIN paperabstracts
        ON papers.PaperId = paperabstracts.PaperId
        LIMIT {limit}
    """

    generator = EmbeddingsGenerator()
    embeddings_file = open("mag_data/mag_embs.pickle", "wb")
    id_to_ind_file = open("mag_data/mag_id_to_ind.pickle", "wb")

    batch_size = 10**6
    batch_ind = 0
    batch_count = 0
    batch = []

    start = time.time()

    with db.cursor(dictionary=True, buffered=True) as dict_cur:
        dict_cur.execute(get_papers_sql)
        print("Done executing")

        for row in dict_cur:
            if batch_ind == batch_size:
                generate_embeddings_and_save(batch, generator, embeddings_file, id_to_ind_file)

                batch = []
                batch_ind = 0
                batch_count += 1

            batch.append(row)
            batch_ind += 1

    print(f"Batch length: {len(batch)}")
    print(f"Batch size: {sys.getsizeof(batch)} bytes")
    generate_embeddings_and_save(batch, generator, embeddings_file, id_to_ind_file)

    embeddings_file.close()
    id_to_ind_file.close()

    end = time.time()

    print(f"Total time {end - start}")

if __name__ == "__main__":
    mem = memory_usage(proc=main)

    print(f"Maximum memory: {max(mem)}")