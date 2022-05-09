import mysql.connector
import pickle
import pandas as pd
import csv

import argparse
import os
import dotenv

from find_papers_by_keyword.assign_paper_keywords import PaperKeywordAssigner
from find_papers_by_keyword.utils import read_pickle_file, read_json_file
from find_papers_by_keyword.utils import gen_sql_in_tup
from find_papers_by_keyword.database import Database
import sql_creds

def main():
    parser = argparse.ArgumentParser(
        description="""
            Command-line utility for loading paper-data for searching.
            First, the paper data is stored to the Publication table.
            Then, keywords are assigned to every paper and stored in the Publication_FoS table.

            The second task requires computing paper embeddings and a mapping from paper ids to the
            row index of the paper's embedding in the embedding matrix. There are two options to do this.
            
            1)  Let the utility compute the embeddings and mapping and store them to a file. To use this
                option, supply the optional arguments --papers_embs_in and --paper_id_to_embs_in, specifying
                the file to store the data in
            2)  Precompute the embeddings and mapping and direct the utility to skip the computation. To use
                this option, supply the optional arguments --papers_embs_out and --paper_id_to_embs_out, specifying
                the location of the data
        """
    )
    parser.add_argument('golden_keywords_file', type=str,
                        help='filepath to csv containing golden keywords data')
    parser.add_argument('keyword_embeddings_file', type=str,
                        help='filepath to json containing paper data')
    parser.add_argument('word_to_other_freq_file', type=str,
                        help='filepath to pickle mapping words to non-CS frequences')
    parser.add_argument('paper_embs_in', type=str,
                        help='filepath to pickle containing paper embeddings')
    parser.add_argument('paper_mapping_in', type=str,
                        help='filepath to json mapping paper ids to embedding-matrix rows')
    parser.add_argument('assignments_out', type=str,
                        help='filepath to csv contains assignments with columns: paper, keyword, score')

    args = parser.parse_args()

    db_conn = mysql.connector.connect(
        host=sql_creds.db_host,
        user=sql_creds.db_user,
        password=sql_creds.db_password,
        database=sql_creds.db_name
    )

    print("Loading and parsing files...")

    golden_keywords_full = pd.read_csv(args.golden_keywords_file)
    golden_keywords = set(golden_keywords_full['word'])

    keyword_embeddings = read_pickle_file(args.keyword_embeddings_file)
    word_to_other_freq = read_pickle_file(args.word_to_other_freq_file)

    database = Database(db_conn)
    keyword_data = database.get_keyword_data()
    
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

    assigner = PaperKeywordAssigner()
    csv_header = ['paper_id', 'keyword_id', 'match_score']

    with open(args.paper_embs_in, "rb") as embs_file, \
         open(args.paper_mapping_in, "rb") as id_to_ind_file, \
         open(args.assignments_out, "w") as assignments_file, \
         mag_db.cursor(dictionary=True) as dict_cur:

        embs = pickle.load(embs_file)
        id_to_ind = pickle.load(id_to_ind_file)

        paper_ids = tuple(id_to_ind.keys())

        csv_out = csv.writer(assignments_file)
        csv_out.writerow(csv_header)

        batch_size = 30000
        batch = 0

        print(len(paper_ids))
        while batch * batch_size < len(paper_ids):
            paper_ids_batch = paper_ids[batch_size * batch: batch_size * (batch + 1)]

            fields_in_sql = gen_sql_in_tup(len(paper_ids_batch))
            get_papers_sql = f"""
                SELECT papers.PaperId as id, papers.PaperTitle as title, paperabstracts.Abstract as abstract 
                FROM papers JOIN paperabstracts ON papers.PaperId = paperabstracts.PaperId
                WHERE papers.PaperId IN {fields_in_sql};
            """

            dict_cur.execute(get_papers_sql, paper_ids_batch)
            papers = dict_cur.fetchall()

            assignments = assigner.assign_paper_keywords(papers, keyword_data, golden_keywords, embs, keyword_embeddings, id_to_ind, word_to_other_freq)
            csv_out.writerows(assignments)

            batch += 1



if __name__ == "__main__":
    main()