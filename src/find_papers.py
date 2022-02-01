from find_papers_by_keyword.paper_search_engine import PaperSearchEngine
from find_papers_by_keyword.database import Database
import mysql.connector
import argparse
import sql_creds


def build_result_string(rank, title, abstract, match_score):
    return f'Paper {rank}\n' + \
        f'Score: {match_score}\n' + \
        f'Title: {title}\n' + \
        f'Abstract: {abstract}\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('keywords', type=str, nargs='+',
                        help='keywords in search query. Separate with spaces')
    args = parser.parse_args()

    db_connection = mysql.connector.connect(
        host=sql_creds.db_host,
        user=sql_creds.db_user,
        password=sql_creds.db_password,
        database=sql_creds.db_name
    )

    engine = PaperSearchEngine(db_connection)
    search_results = engine.get_relevant_papers(
        args.keywords, 15)

    print(f"{len(search_results)} papers found\n")

    for i, result in enumerate(search_results):
        rank = i + 1
        id, title, abstract, match_score = result

        print(
            f'Paper {rank}:\tID: {id}\n' + \
            f'Score: {match_score}\n' + \
            f'Title: {title}\n' + \
            f'Abstract: {abstract}\n'
        )
        rank += 1

    db_connection.close()


if __name__ == "__main__":
    main()
