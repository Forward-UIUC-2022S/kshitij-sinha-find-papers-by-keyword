from find_papers_by_keyword.paper_search_engine import PaperSearchEngine
import database.db_conn_factory as db_factory
import argparse


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

    db_connection = db_factory.get_forward_db()

    engine = PaperSearchEngine(db_connection)
    search_results = engine.get_relevant_papers(
        args.keywords, 15)

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
