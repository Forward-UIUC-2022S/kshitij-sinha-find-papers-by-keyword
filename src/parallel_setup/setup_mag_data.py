import sys
import json
import pickle

import src.database.db_conn_factory as db_factory

def main():
    mag_conn = db_factory.get_azure_mag_db()
    forward_conn = db_factory.get_forward_db()

    limit = sys.argv[1]

    move_mag_data(mag_conn, forward_conn, limit)
    save_keyword_json(forward_conn)
    save_ids(forward_conn)

def move_mag_data(mag_db_conn, forward_db_conn, limit):
    """
    Moves data from MAG database to the user's assignment database (forward database)

    Args:
        -limit: the number of papers to move from MAG to Forward
    """
    with mag_db_conn.cursor() as mag_cur, forward_db_conn.cursor() as forward_cur:
        get_papers_sql = f"""
            SELECT papers.PaperId as id, papers.PaperTitle as title, paperabstracts.Abstract as abstract , CitationCount as citations
            FROM papers JOIN paperabstracts ON papers.PaperId = paperabstracts.PaperId
            LIMIT {limit}
        """

        mag_cur.execute(get_papers_sql)
        paper_data = mag_cur.fetchall()

        print(f"Fetched {len(paper_data)} from Azure")

        save_papers_sql = """
            REPLACE INTO Publication (id, title, abstract, citations)
            VALUES (%s, %s, %s, %s)
        """
        forward_cur.executemany(save_papers_sql, paper_data)
        forward_db_conn.commit()

        print(f"Done saving to Forward")

def save_keyword_json(forward_db):
    """
    Gets keyword data from a database and stores it in the following JSON format:
        [
            {
                "id": int,
                "keyword": str
            },
            ...
        ]
    The JSON is saved to data/db_keywords.json

    Args:
        - forward_db: A database connection containing keyword data

    * This script may not be required in the future. It is being used now because MAG
    embeddings are being generated on an Azure server that does not have access to the 
    Forward databse. To get around this, the keyword data is extracted into a file and
    moved to the Azure server so the server doesn't have to rely on a Forward database.
    """

    json_filepath = "data/db_keywords.json"
    sql = "SELECT id, keyword FROM FoS"

    with forward_db.cursor(dictionary = True) as cur, \
        open(json_filepath, "w") as json_file:

        print("Fetching keywords from database")
        cur.execute(sql)
        keywords = cur.fetchall()

        print(f"Saving {len(keywords)} keywords to {json_filepath}")
        json.dump(keywords, json_file)

def save_ids(forward_db):
    """
    Saves all Paper IDS to a file (data/PaperIds.pickle) for quick batching

    Args:
        - forward_db: A database containing paper data stored in 'Publication' table.

    """

    id_file = "data/PaperIds.pickle"
    sql = "SELECT id FROM Publication"

    with forward_db.cursor() as cur, open(id_file, "wb") as out_file:
        cur.execute(sql)
        ids = cur.fetchall()
        ids = sorted([int(i[0]) for i in ids])

        print(f"Saving {len(ids)} paper ids to data/PaperIds.pickle")
        pickle.dump(ids, out_file)
        

if __name__ == "__main__":
    main()