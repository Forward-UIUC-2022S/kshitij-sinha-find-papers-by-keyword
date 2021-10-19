import math
import numpy as np
import pandas as pd
import mysql.connector
import numpy.linalg as la
from sklearn.cluster import DBSCAN

from trie import construct_trie, construct_re, get_matches
from utils import read_pickle_file, get_top_k, concat_paper_info, standardize_non_ascii

def normalize_embs(emb_arr):
    emb_norms = la.norm(emb_arr, axis=1)
    return emb_arr / emb_norms[:,None]

def normalize_vec(vec):
    return vec / la.norm(vec)


data_root_dir = '../data/'

keyword_metadata_file = data_root_dir + "springer_keyword_data.pickle"
paper_metadata_file = data_root_dir + "SB_filtered_paper_data.pickle"

# ids_file = data_root_dir + "springer_word_to_id.pickle"     
golden_keywords_file = data_root_dir + "golden_words.csv" 

# word_to_other_freq_file = data_root_dir + "other_freqs.pickle"  # Incomplete. Available in "Keyword-Springer-83K"

paper_embeddings_file = data_root_dir + "SB_paper_embeddings.pickle"    # Complete
# paper_ids_file = data_root_dir + "SB_paper_embedding_mag_ids.pickle"    # Complete

keyword_embeddings_file = data_root_dir + "springer_keyword_embs.pickle"   # Complete


### Reading data from files ###
print("Loading and preprocessing data")

keyword_metadata = read_pickle_file(keyword_metadata_file)
paper_metadata = read_pickle_file(paper_metadata_file)

# paper_ids = read_pickle_file(paper_ids_file)
paper_embeddings = read_pickle_file(paper_embeddings_file)
# word_to_id = read_pickle_file(ids_file)

# Frequency counts of keywords for non-cs papers from arxiv
# word_to_other_freq = read_pickle_file(word_to_other_freq_file)

keyword_embeddings = read_pickle_file(keyword_embeddings_file)
keyword_embeddings = normalize_embs(keyword_embeddings)

print(paper_embeddings.shape)
print(keyword_embeddings.shape)

# Database connection
# mydb = mysql.connector.connect(
#   host="localhost",
#   user="sandbox",
#   password="sandbox",
#   database="assign_paper_kwds"
# )
# mycursor = mydb.cursor()

# mycursor.execute("""
#     SELECT id, title, abstract
#     FROM Publication
#     WHERE abstract IS NOT NULL
# """)
# papers = mycursor.fetchall()

"""
Keyword set formed from the set intersection of
- Springer set: parse papers for author-labeled keywords and keep those
with freq >= 5
- EmbedRank set: Use EmbedRank to extract keywords from entire cs corpus.
"""
golden_keywords_full = pd.read_csv(golden_keywords_file)
golden_keywords = set(golden_keywords_full['word'])


# paper_id_to_idx = {}
# for i in range(len(paper_ids)):
#     paper_id_to_idx[paper_ids[i]] = i

keywords_trie = construct_trie(golden_keywords)
keywords_re = construct_re(keywords_trie)
print("Starting paper keyword extraction: ")

p_i = 0
# For every paper, finds top keyword matches. Stores matches in database
# Every row in database has paper, keyword, and match score
# For every paper, removes duplicate keywords using clustering
for paper in paper_metadata:
    # paper_id = paper[0]
    raw_text = concat_paper_info(paper['title'], paper['abstract'])
    print(raw_text)

    # Get candidate keywords by checking occurrence
    keyword_matches = get_matches(raw_text, keywords_re, True)
    print(len(keyword_matches))
    if len(keyword_matches) == 0:
        continue
    # try:
        # Keyword_matches stored as [(<keyword>, <id>), ...]
    match_ids = list(map(lambda t: keyword_metadata[t]['index'], keyword_matches))
    # except KeyError:
    #     continue
    # except Exception as e:
    #     print("Exception", type(e), e)
        # match_ids = list(map(lambda t: word_to_id[standardize_non_ascii(t[0])], keyword_matches))

    match_embs = keyword_embeddings[match_ids]
    print("here")
    print(match_embs)


    # try:
    #     paper_embedding = paper_embeddings[paper_id_to_idx[paper_id]]
    # except KeyError:
    #     continue

    # paper_embedding = normalize_vec(paper_embedding)

    # sim_scores = np.dot(match_embs, paper_embedding.T)

    # keyword_scores = []
    # for i in range(len(match_ids)):
    #     m_t = keyword_matches[i]
    #     keyword = m_t[0]

    #     kw_score = sim_scores[i]

    #     # Checking if current keyword appears in non-cs papers in arxiv corpus
    #     if keyword in word_to_other_freq:
    #         other_freq = word_to_other_freq[keyword]

    #         # Penalize general words
    #         if other_freq >= 1000:
    #             kw_score /= math.sqrt(other_freq)

    #     kw_t = (match_ids[i], kw_score)
    #     keyword_scores.append(kw_t)


    # # Select top-k-scoring keywords
    # max_keywords = 9
    # query_keywords = 17
    # top_keywords = get_top_k(keyword_scores, min(query_keywords, len(keyword_scores) - 1), lambda t: t[1])

    # selected_keyword_ids = [t[0] for t in top_keywords]
    # selected_keyword_embs = keyword_embeddings[selected_keyword_ids]


    # # Removing dupicate keywords
    # db = DBSCAN(eps=0.47815, min_samples=2).fit(selected_keyword_embs)
    # labels = db.labels_

    # curr_groups = set()
    # unique_top_keywords = []

    # for i in range(len(top_keywords)):
    #     if len(unique_top_keywords) >= max_keywords:
    #         break

    #     group_idx = labels[i]

    #     if group_idx == -1:
    #         unique_top_keywords.append(top_keywords[i])
    #     elif group_idx not in curr_groups:
    #         curr_groups.add(group_idx)
    #         unique_top_keywords.append(top_keywords[i])

    # top_keywords = unique_top_keywords
    # # print("The top keywords: ", top_keywords)
    # # print("-" * 10)

    # # Insert data into db
    # for kw_t in top_keywords:
    #     keyword_id = str(kw_t[0])
    #     keyword_score = str(kw_t[1])
    #     insert_sql = "REPLACE INTO Publication_FoS (publication_id, FoS_id, score) VALUES (%s, %s, %s)"
    #     mycursor.execute(insert_sql, [paper_id, keyword_id, keyword_score])

    # mydb.commit()


    # if p_i % 1000 == 0:
    #     print("On " + str(p_i) + "th paper")
    p_i += 1

    if p_i == 3:
        break