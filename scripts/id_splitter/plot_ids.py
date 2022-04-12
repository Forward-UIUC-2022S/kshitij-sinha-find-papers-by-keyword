import matplotlib.pyplot as plt
import pickle

with open("data/PaperIds.pickle", "rb") as p:
    ids = pickle.load(p)

print("Loaded")
print(len(ids))
plt.hist(ids[:100])
plt.savefig("fig.png", format="png")