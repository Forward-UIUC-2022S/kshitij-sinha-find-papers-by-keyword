import mysql.connector
import sys
import os
import dotenv

from parallel_mag_embs_generator import ParallelMagEmbsGenerator

def compute_chunk(server_count, server_id):
    import pickle

    with open("data/PaperIds.pickle", "rb") as p:
        ids = pickle.load(p)

    chunk_size = int(len(ids) / server_count)
    low = chunk_size * server_id
    high = min(low + chunk_size, len(ids) - 1)
    return ids[low], ids[high]
    

def main():
    server_count = int(sys.argv[1])
    server_id = int(sys.argv[2])

    dotenv.load_dotenv()

    mag_db = mysql.connector.connect(
        user=os.getenv('MAG_USER'), 
        password=os.getenv('MAG_PASS'), 
        host=os.getenv("MAG_HOST"), 
        port=3306, 
        database=os.getenv('MAG_DB'), 
        ssl_ca="DigiCertGlobalRootCA.crt.pem", 
        ssl_disabled=False
    )

    low_lim, high_lim = compute_chunk(server_count, server_id)

    batch_size = 100000

    generator = ParallelMagEmbsGenerator(mag_db)

    embeddings_file = open("mag_data/mag_embs.pickle", "wb")
    id_to_ind_file = open("mag_data/mag_id_to_ind.pickle", "wb")

    generator.generate_embs(low_lim, high_lim, batch_size, embeddings_file, id_to_ind_file)

    embeddings_file.close()
    id_to_ind_file.close()

if __name__ == "__main__":
    main()