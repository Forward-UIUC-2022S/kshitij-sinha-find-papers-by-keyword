import math
import numpy as np
import pandas as pd
import mysql.connector
import numpy.linalg as la
from sklearn.cluster import DBSCAN

from src.trie.utils import construct_trie, construct_re, get_matches
from src.utils import read_pickle_file, read_json_file, get_top_k, concat_paper_info, standardize_non_ascii


class PaperKeywordAssigner():
    def __init__(self, db):
        self.db = db

    def assign_paper_keywords(
            self, golden_keywords_file, paper_embeddings_file,
            paper_id_to_embeddings_file, keyword_embeddings_file, word_to_other_freq_file):
        ### Reading data from files ###
        print("Loading and preprocessing data")
        with self.db.cursor(dictionary=True) as dictcursor:
            paper_metadata = self._get_paper_data(dictcursor)
            keyword_metadata = self._get_keyword_data(dictcursor)

        keyword_to_id = {k["keyword"]: k["id"] for k in keyword_metadata}

        paper_embeddings = read_pickle_file(paper_embeddings_file)
        paper_id_to_emb_ind = read_json_file(paper_id_to_embeddings_file)

        keyword_embeddings = read_pickle_file(keyword_embeddings_file)
        keyword_embeddings = self._normalize_embs(keyword_embeddings)

        # Frequency counts of keywords for non-cs papers from arxiv
        word_to_other_freq = read_pickle_file(word_to_other_freq_file)
        word_id_to_other_freq = self._get_word_id_to_other_freq(
            word_to_other_freq, keyword_to_id)

        """
        Keyword set formed from the set intersection of
        - Springer set: parse papers for author-labeled keywords and keep those
        with freq >= 5
        - EmbedRank set: Use EmbedRank to extract keywords from entire cs corpus.
        """
        golden_keywords_full = pd.read_csv(golden_keywords_file)
        golden_keywords = set(golden_keywords_full['word'])

        keywords_trie = construct_trie(golden_keywords)
        keywords_re = construct_re(keywords_trie)

        # For every paper, finds top keyword matches. Stores matches in database
        # Every row in database has paper, keyword, and match score
        # For every paper, removes duplicate keywords using clustering
        cursor = self.db.cursor()
        print("Starting paper keyword extraction: ")
        for p_i, paper in enumerate(paper_metadata):
            paper_id = paper['id']
            raw_text = concat_paper_info(paper['title'], paper['abstract'])

            paper_embedding_ind = paper_id_to_emb_ind[paper_id]
            paper_embedding = paper_embeddings[paper_embedding_ind]
            paper_embedding = self._normalize_vec(paper_embedding)

            match_ids = self._get_keyword_match_ids(
                raw_text, keywords_re, keyword_to_id)
            # Uses assmuption that ids are the indices of the embedding
            match_embs = keyword_embeddings[match_ids]
            # Compute dot of every match embedding with this paper's embedding
            sim_scores = np.dot(match_embs, paper_embedding)

            keyword_scores = self._get_penalized_keyword_scores(zip(match_ids, sim_scores), word_id_to_other_freq)

            # Select top-k-scoring keywords
            query_keywords = 17
            top_keywords = get_top_k(keyword_scores, min(
                query_keywords, len(keyword_scores) - 1), lambda t: t[1])

            selected_keyword_ids = [t[0] for t in top_keywords]
            selected_keyword_embs = keyword_embeddings[selected_keyword_ids]

            max_keywords = 9
            unique_top_keywords = self._get_unique_keywords(top_keywords, selected_keyword_embs, max_keywords)

            self._add_paper_assignments_to_database(cursor, paper_id, unique_top_keywords)

            if p_i % 1000 == 0:
                print("On " + str(p_i) + "th paper")

        cursor.close()
        print(f"{p_i} papers analyzed")
        self.db.commit()

    def _add_paper_assignments_to_database(self, cur, paper_id, keywords):
        """
        Adds rows to MySQL database

        Arguments:
        - cur: mysql.connector database cursor
        - paper_id: the id of the paper for which keywords have been assigned
        - keywords: a list of tuples with the format (keyword_id, keyword_score) that have been assigned
        to the paper

        Returns:
        - None. A adds rows to the database for the columns Publication_id, FoS_id, score. For the i'th row,
        these columns correspond to the inputs paper_id, keywords[i][0], keywords[i][1], respectively
        """
        for keyword_id, keyword_score in keywords:
            keyword_id = str(keyword_id)
            keyword_score = str(keyword_score)
            insert_sql = "REPLACE INTO Publication_FoS (publication_id, FoS_id, score) VALUES (%s, %s, %s)"
            cur.execute(insert_sql, [paper_id, keyword_id, keyword_score])

    def _get_unique_keywords(self, keywords, embeddings, max_keywords):
        """
        Retruns a list of keywords that are mathematically unique using DBSCAN clustering.
        The input embedding vectors will be grouped into clusters using DBSCAN. Out of every cluster,
        only one representative keyword will be retreieved and returned from this method, up to a total
        of "max_keywords" returned.

        Arguments:
        - keywords: A list of keywords
        - embeddings: A list of keyword embeddings. This list should be parallel to keywords.
        - max_keywords: The maximum unique keywords to retrieve. The length of the returned list
        will be no greater than max keywords

        Returns:
        - A list of keywords that is a subset of the input, "keywords." These keywords are each unique
        from each other, based on DBSCAN clustering. 
        """
        db = DBSCAN(eps=0.47815, min_samples=2).fit(embeddings)
        labels = db.labels_

        curr_groups = set()
        unique_top_keywords = []

        for i, keyword in enumerate(keywords):
            if len(unique_top_keywords) >= max_keywords:
                break

            group_idx = labels[i]

            if group_idx == -1:
                unique_top_keywords.append(keyword)
            elif group_idx not in curr_groups:
                curr_groups.add(group_idx)
                unique_top_keywords.append(keyword)

        return unique_top_keywords

    def _get_penalized_keyword_scores(self, matches, word_id_to_other_freq):
        """
        Returns a tuple of keyword/score pairs, but penalizes keyword matches that appear frequently (more than 1000 times) in non-CS papers.
        For such keywords, the keyword score is divided by its square root

        Arguments:
        - matches: A list of tuples representing matches. Every tuple should be in the format (keyword_id, match_score), where match_score is the
        similarity score betwen keyword_id and a paper.
        The i'th element of match_scores should be the score corresponding to the i'th element of keyword_ids
        - word_id_to_other__freq: a dictionary mapping a keyword to its frequency in non-CS papers. The keys of this dictionary are keyword ids

        Returns:
        - A list of tuples in the same format as the input argument "matches". However, the return list contains penalized match scores based on
        the specification above
        """
        # Keyword scores will be stored as: (<keyword_id, match_score>, ...)
        keyword_scores = []
        for match_id, kw_score in matches:
            # Checking if current keyword appears in non-cs papers in arxiv corpus
            if match_id in word_id_to_other_freq:
                other_freq = word_id_to_other_freq[match_id]

                # Penalize general words
                if other_freq >= 1000:
                    kw_score /= math.sqrt(other_freq)

            kw_t = (match_id, kw_score)
            keyword_scores.append(kw_t)

        return keyword_scores

    def _get_keyword_match_ids(self, raw_text, keywords_re, keyword_to_id: dict):
        """
        Finds all keywords that appear in raw_text and returns the ids of the matched keywords
        """
        # Get candidate keywords by checking occurrence
        keyword_matches = get_matches(raw_text, keywords_re, True)
        match_ids = []
        for keyword, match_freq in keyword_matches:
            if keyword in keyword_to_id:
                match_ids.append(keyword_to_id[keyword])

            # if match is not in keyword_to_id, then match doesn't exist in our original keyword dataset
            # so we skip the corresponding matched keyword

        return match_ids

    def _get_word_id_to_other_freq(self, word_to_other_freqs, word_to_id):
        """
        Converts a map from words to frequencies into a map of word ids to other frequcies
        """
        word_id_to_other_freq = {}
        for word, freq in word_to_other_freqs.items():
            if word in word_to_id:
                word_id_to_other_freq[word_to_id[word]] = freq

            # If word is not in word_to_id, then word doesn't exist in our keyword dataset and will never
            # be matched with a paper. We can skip adding this word to the dictionary

        return word_id_to_other_freq

    def _get_paper_data(self, dictcursor):
        dictcursor.execute("""
            SELECT id, title, abstract
            FROM Publication
        """)
        return dictcursor.fetchall()

    def _get_keyword_data(self, dictcursor):
        dictcursor.execute("""
            SELECT id, keyword
            FROM FoS
        """)
        return dictcursor.fetchall()

    def _normalize_embs(self, emb_arr):
        emb_norms = la.norm(emb_arr, axis=1)
        return emb_arr / emb_norms[:, None]

    def _normalize_vec(self, vec):
        return vec / la.norm(vec)


def main():
    mydb = mysql.connector.connect(
        host="localhost",
        user="forward",
        password="forward",
        database="assign_1"
    )

    data_root_dir = 'data/'

    golden_keywords_file = data_root_dir + "golden_words.csv"

    paper_embeddings_file = data_root_dir + "paper_embs.pickle"
    paper_id_to_embeddings_file = data_root_dir + "paper_id_to_ind.json"
    keyword_embeddings_file = data_root_dir + "keyword_embs.pickle"

    word_to_other_freq_file = data_root_dir + "other_freqs.pickle"

    assigner = PaperKeywordAssigner(mydb)
    assigner.assign_paper_keywords(golden_keywords_file, paper_embeddings_file,
                                   paper_id_to_embeddings_file, keyword_embeddings_file,
                                   word_to_other_freq_file)


if __name__ == "__main__":
    main()
