from find_papers_by_keyword.embeddings_generator import EmbeddingsGenerator
import pickle
import mysql.connector
import sys

class ParallelMagEmbsGenerator:
    def __init__(self, db):
        self._db = db
        self._generator = EmbeddingsGenerator()

    def _generate_embeddings_and_save(self, batch, generator, embs_file, id_to_ind_file):
        embs, id_to_ind = generator.generate_paper_embeddings(batch)
        pickle.dump(embs, embs_file)
        pickle.dump(id_to_ind, id_to_ind_file)

    def generate_embs(self, low_id_lim, high_id_lim, batch_size, embeddings_file, id_to_ind_file):
        # Server_id in [0, server_count)
        get_papers_sql = f"""
        SELECT papers.PaperId AS id, papers.PaperTitle AS title, paperabstracts.Abstract AS abstract
        FROM papers
        JOIN paperabstracts
        ON papers.PaperId = paperabstracts.PaperId
        WHERE papers.PaperId BETWEEN {low_id_lim} AND {high_id_lim}
        """

        print(f"Generating embeddings for ID's between {low_id_lim} and {high_id_lim}")

        with self._db.cursor(dictionary=True) as dict_cur:
            dict_cur.execute(get_papers_sql)
            batch = dict_cur.fetchmany(batch_size)
            while batch:
                self._generate_embeddings_and_save(batch, self._generator, embeddings_file, id_to_ind_file)
                batch = dict_cur.fetchmany(batch_size)
