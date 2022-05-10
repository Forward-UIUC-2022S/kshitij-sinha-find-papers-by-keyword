import pandas as pd
import numpy as np
import json
import sys
import os

inFile = sys.argv[1]
outFile = sys.argv[2]


def _get_abstract_from_IA(index_length, inverted_index):
    token_list = [None] * index_length
    for token in inverted_index:
        for ind in inverted_index[token]:
            token_list[ind] = token
    token_list = list(filter(None, token_list))
    abstract = u' '.join(token_list)
    return abstract


def convert(row):
        indexed_abstract = row['IndexedAbstract']
        index_json = json.loads(indexed_abstract)
        index_length = index_json['IndexLength']
        inverted_index = index_json['InvertedIndex']

        return  _get_abstract_from_IA(index_length, inverted_index)

nrows = 10**4
chunksize = 4
iters = nrows / chunksize


header = True
if os.path.exists(outFile):
  os.remove(outFile)
reader = pd.read_csv(inFile, sep='\t', names=['id', 'IndexedAbstract'], chunksize=4)
for i, df in enumerate(reader):
    converted_df = pd.concat([df['id'], df.apply(convert, axis=1)], axis=1, keys=['id', 'Abstract'])
    converted_df.to_csv(outFile, index=False, mode='a', header = header)

    header = False

    if i >= iters:
        break