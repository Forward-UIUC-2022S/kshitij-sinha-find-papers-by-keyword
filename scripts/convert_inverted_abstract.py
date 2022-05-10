import pandas as pd
import numpy as np
import json
import sys
import time

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


df = pd.read_csv(inFile, sep='\t', names=['id', 'IndexedAbstract'], nrows = 10**4)


df['Abstract'] = df.apply(convert, axis=1)
converted_df = df[['id', 'Abstract']]
converted_df.to_csv(outFile, index=False)