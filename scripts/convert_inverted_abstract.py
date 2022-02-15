import pandas as pd
import numpy as np
import json
import sys

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

df = pd.read_csv(inFile, sep='\t', names=['id', 'IndexedAbstract'])
df['Abstract']=['']*len(df)

for i in range(len(df)):
    indexed_abstract = df['IndexedAbstract'][i]
    index_json = json.loads(indexed_abstract)
    index_length = index_json['IndexLength']
    inverted_index = index_json['InvertedIndex']
    
    df.at[i, 'Abstract'] = _get_abstract_from_IA(index_length, inverted_index)

converted_df = df[['id', 'Abstract']]
converted_df.to_csv(outFile, index=False)