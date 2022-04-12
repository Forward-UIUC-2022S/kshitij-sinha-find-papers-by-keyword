from find_papers_by_keyword.embeddings_generator import EmbeddingsGenerator
import pickle
import mysql.connector

class ParallelMagEmbsGenerator:
    def __init__(self, db, server_count, first_id, last_id):
        # Assumes uniform distribution of ids on [first_id, last_id]
        self._db = db
        self._generator = EmbeddingsGenerator()
        self._server_count = server_count
        self._first_id = first_id
        self._after_last_id = last_id + 1

    def _generate_embeddings_and_save(self, batch, generator, embs_file, id_to_ind_file):
        embs, id_to_ind = generator.generate_paper_embeddings(batch)
        pickle.dump(embs, embs_file)
        pickle.dump(id_to_ind, id_to_ind_file)

    def generate_embs(self, server_id, batch_size, embeddings_file, id_to_ind_file):
        # Server_id in [0, server_count)
        low_id_lim = int(server_id * (self._after_last_id / self._server_count))
        high_id_lim = int((server_id + 1) * (self._after_last_id / self._server_count)) - 1

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