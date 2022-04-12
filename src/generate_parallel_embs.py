import mysql.connector
import json
import pickle
import sys
import os
import dotenv
import sql_creds

from parallel_mag_embs_generator import ParallelMagEmbsGenerator

from memory_profiler import profile, memory_usage
import time

def main():
    dotenv.load_dotenv()

    mag_db = mysql.connector.connect(
        user=os.getenv('MYSQL_USER'), 
        password=os.getenv('MYSQL_PASS'), 
        host="mag-2020-09-14.mysql.database.azure.com", 
        port=3306, 
        database=os.getenv('MYSQL_DB'), 
        ssl_ca="DigiCertGlobalRootCA.crt.pem", 
        ssl_disabled=False
    )

    smallest_id = 9
    largest_id = 3084441008

    batch_size = 100000

    generator = ParallelMagEmbsGenerator(mag_db, 100, smallest_id, largest_id)

    embeddings_file = open("mag_data/mag_embs.pickle", "wb")
    id_to_ind_file = open("mag_data/mag_id_to_ind.pickle", "wb")

    generator.generate_embs(0, batch_size, embeddings_file, id_to_ind_file)

    embeddings_file.close()
    id_to_ind_file.close()

if __name__ == "__main__":
    main()