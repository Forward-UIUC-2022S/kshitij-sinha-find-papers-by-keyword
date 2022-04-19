"""
Create small pickle file containing list [1 ... 100000)
This can be used to test embedding generation on a uniform chunk of papers
Requires directory small_data
"""

import pickle

ids = list(range(10000000))

with open("small_data/PaperIds.pickle", "wb") as f:
    ids = pickle.dump(ids, f)

