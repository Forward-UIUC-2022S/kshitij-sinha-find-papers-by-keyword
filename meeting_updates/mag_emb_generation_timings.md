These are timings for generating paper embeddings for MAG papers. There are a total of 242,996,164 papers in the MAG dataset

Embeddings were analyzed in batches to limit memory usage. Tehse batches were created in two ways:
1) Raw Python code were papers were manually appended to a list representing a batch
2) Using the mysql.connector fetchmany() function

## 1) Raw Python
Here, a set number of papers were ana

| Papers | Papers per batch | Batches | Execution time | Memory (MiB) |
| - | - | - | - | - |
| 10<sup>4</sup> | 10<sup>2</sup> | 10<sup>2</sup> | 23.285s | 5234
| 10<sup>4</sup> | 10<sup>3</sup> | 10<sup>2</sup> | 23.624 | 5174
| 10<sup>4</sup> | 10<sup>4</sup> | 1 | 22.556 | 5223.789
| 10<sup>5</sup> | 10<sup>3</sup> | 10<sup>2</sup> | 2m 32.682s |
| 10<sup>5</sup> | 10<sup>5</sup> | 1 | 2m 36.131s | 
| 10<sup>6</sup> | 10<sup>6</sup> | 1 | 35m 13.074s | 17655.72
| 10<sup>7</sup> | 10<sup>6</sup> | 10 | 10h 15m 35s | 29847.72

## 2) Fetchmany
| Papers | Papers per batch | Batches | Execution time | Memory (MiB) |
| - | - | - | - | - |
| 10<sup>4</sup> | 10<sup>2</sup> | 10<sup>2</sup> | 26.294s | 5603.379
| 10<sup>5</sup> | 10<sup>5</sup> | 1 | 3m 20s | 6109.5625