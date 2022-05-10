import src.database.db_conn_factory as db_factory
import sys

mag_conn = db_factory.get_azure_mag_db()
forward_conn = db_factory.get_forward_db()

limit = sys.argv[1]

with mag_conn.cursor() as mag_cur, forward_conn.cursor() as forward_cur:
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
    forward_conn.commit()

    print(f"Done saving to Owl")

