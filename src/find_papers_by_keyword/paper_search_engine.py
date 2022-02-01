from .utils import gen_sql_in_tup, drop_table
import mysql.connector

class PaperSearchEngine:
    def __init__(self, db: mysql.connector.MySQLConnection):
        self.db = db

    def get_relevant_papers(self, keywords: tuple, search_limit):
        """
        Finds top papers that match a set of query keywords and returns them as a list,
        sorted in descending order by match scores

        Arguments:
        - cur: db cursor
        - keywords: a tuple of keywords in our search query
        - search_limit: an integer specifying the number of top publication matches to return

        Returns:
        - A list of tuples representing our search results. Every tuple following the format (paper_id, match_score)
        """
        fields_in_sql = gen_sql_in_tup(len(keywords))
        get_ids_sql =  'SELECT id FROM FoS WHERE keyword IN ' + fields_in_sql + ';'

        with self.db.cursor() as cur:
            cur.execute(get_ids_sql, keywords)
            result = cur.fetchall()
            keyword_ids = tuple(row_tuple[0] for row_tuple in result)

        if len(keyword_ids) == 0:
            # No matching keywords were found, search cannot be completed
            return []
        else:
            self.get_relevant_papers_by_id(keyword_ids, search_limit)

    def get_relevant_papers_by_id(self, keyword_ids: tuple, search_limit):
        """
        Finds top papers that match a set of query keywords and returns them as a list,
        sorted in descending order by match scores

        Arguments:
        - cur: db cursor
        - keywords: a tuple of keyword ids corresponding to keywords in our search query
        - search_limit: an integer specifying the number of top publication matches to return

        Returns:
        - A list of tuples representing our search results. Every tuple following the format 
            (paper_id, title, abstract, match_score)
        """
        with self.db.cursor() as cur:
            self._store_keywords(cur, keyword_ids)
            return self._get_ranked_publications(cur)[:search_limit]

    def compute_match_score(self, paper_id, keyword_id):
        sql = """
            SELECT score
            FROM Publication_FoS
            WHERE Publication_id = (%s) AND FoS_id = (%s)
        """
        with self.db.cursor() as cur:
            cur.execute(sql, (paper_id, keyword_id))
            return cur.fetchone()[0]

    def _get_ranked_publications(self, cur):
        """
        Computes keyword match scores for every publication and returns a list of publications
        sorted in decreasing order of match score. 
        Requires Top_Keywords table to exist, which is created by _store_keywords method

        Arguments:
        - cur: db cursor
        - search_limit: an integer specifying the number of top publication matches to return

        Returns: A ranked list of tuples representing matched papers and their corresponding match score.
        The list uses the following schema:
            [(id_1, title_1, absract_1, paper_score_1), (id_2, title_2, abstract_2 ,paper_score_2), ...]

        Each publication has an associated score for each input keyword.
        The score between an input keyword and a paper is computed by determining if 
        there is any match between the top ten similar keywords for the input keyword 
        and the paper's keyword assignments (see assign_paper_kwds.py for details on
        how keywords are assigned to papers). The final score between a keyword and
        a publication is the product of similairty of the keyword to the publication
        and the npmi score describing the similarity of the keyword to the input keyword.
        This product is store as max_score.

        The total_score for a paper is the sum of max_scores for every keyword in the input query.
        The final score for a paper (paper_score) is computed as total_score * citation.
        """

        # Some keywords are never paired with publications in assign_paper_kwds.py
        # Thus, some similar keywords are matched with NULL publication rows
        # To fix this, we use an INNER JOIN when finding joining with Publication_FoS
        drop_table(cur, "Publication_Rank_Scores")
        get_ranked_publications_sql = """
            SELECT Publication_id, title, abstract, SUM(max_score) * (citations + 1) as total_score
            FROM
                (
                SELECT parent_id, Publication_id, MAX(npmi * score) as max_score

                FROM Top_Keywords
                JOIN Publication_FoS ON id = Publication_FoS.FoS_id

                GROUP BY parent_id, Publication_id
                ) as keyword_paper_score
            LEFT JOIN Publication on Publication_id = Publication.id
            GROUP BY Publication_id
            ORDER BY total_score DESC
        """
        cur.execute(get_ranked_publications_sql)
        return cur.fetchall()

    
    def _store_keywords(self, cur, keyword_ids: tuple):
        """
        Stores top 10 similar keywords for each input keyword

        Arguments:
        - keyword_ids: list of ids of input keywords
        - cur: db cursor

        Returns: None. Each entry in Top_Keywords table is of the form (parent_id, keyword_id, npmi).
        - parent_id: id of the original input keyword
        - keyword_id: id of similar keyword
        - npmi is a similarity score between the two keywords
        Note: the identity row for each keyword_id is included by default with
        similarity score 1 (i.e. for each kw_id in keywords_ids, there will be a
        row in Top_Keywords of (kw_id, kw_id, 1))
        """
        fields_in_sql = gen_sql_in_tup(len(keyword_ids))

        drop_table(cur, "Top_Keywords")
        get_related_keywords_sql = """
            
            CREATE TABLE Top_Keywords (
                parent_id INT,
                id INT,
                npmi DOUBLE,
                PRIMARY KEY(parent_id, id)
            )
            SELECT parent_id, id, npmi
            FROM
            (
                SELECT parent_id, id, npmi,
                @kw_rank := IF(@current_parent = parent_id, @kw_rank + 1, 1) AS kw_rank,
                @current_parent := parent_id
                FROM
                (
                    (SELECT id2 AS parent_id,
                    id1 AS id, npmi
                    FROM FoS_npmi_Springer
                    WHERE id2 IN """ + fields_in_sql + """)
                    UNION
                    (SELECT
                    id1 AS parent_id,
                    id2 as id, npmi
                    FROM FoS_npmi_Springer
                    WHERE id1 IN """ + fields_in_sql + """)
                ) as top_keywords
                ORDER BY parent_id, npmi DESC
            ) AS ranked_keywords
            WHERE kw_rank <= 10
        """
        get_related_query_params = 2 * keyword_ids
        cur.execute(get_related_keywords_sql, get_related_query_params)

        append_given_sql = """
            INSERT INTO Top_Keywords
            (parent_id, id, npmi)
            VALUES
            """ + ",\n".join(["(%s, %s, 1)"] * len(keyword_ids))

        append_given_query_params = [id for id in keyword_ids for i in range(2)]

        cur.execute(append_given_sql, append_given_query_params)
        self.db.commit()