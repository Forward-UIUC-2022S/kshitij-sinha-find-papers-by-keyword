import matplotlib.pyplot as plt
import json
import pickle

with open("data/PaperIds.json") as f, open("data/PaperIds.pickle", "w") as p:
    ids = json.load(f)
    print(type(ids))
    print(type(list(ids)))
    pickle.dump(list(ids))

# print(ids)