import matplotlib.pyplot as plt
import pickle

with open("data/PaperIds.pickle", "rb") as p:
    ids = pickle.load(p)

print(f"Max {max(ids)}")
print(f"Min {min(ids)}")