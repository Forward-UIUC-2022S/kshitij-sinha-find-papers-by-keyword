import sys

from find_papers_by_keyword.parallel_mag_embs_generator import ParallelMagEmbsGenerator
import  database.db_conn_factory as db_factory

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

    mag_db = db_factory.get_azure_mag_db()

    low_lim, high_lim = compute_chunk(server_count, server_id)
    batch_size = 100000
    generator = ParallelMagEmbsGenerator(mag_db)

    with open("mag_data/mag_embs.pickle", "wb") as embeddings_file, \
         open("mag_data/mag_id_to_ind.pickle", "wb") as id_to_ind_file:
        generator.generate_embs(low_lim, high_lim, batch_size, embeddings_file, id_to_ind_file)

if __name__ == "__main__":
    main()