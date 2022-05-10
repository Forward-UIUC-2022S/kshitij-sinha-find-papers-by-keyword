# import pandas as pd

import csv
import sys
import csv

class MagPaperReader():
    def __init__(self):
        pass

    def load_paper_file(paper_file):
        pass


def main():
    maxInt = sys.maxsize
    csv.field_size_limit(maxInt)

    file = "/scratch/pritom/mag-2020-09-14/mag/Papers.txt"
    # headers =  ['PaperId','Doi','PaperTitle','CitationCount']

    with open(file, 'r') as f:
        tabin = csv.reader(f, dialect=csv.excel_tab)
        for i in range(10**10):
            try:
                next(tabin)
            except csv.Error as error:
                print(i)
                print(error)
        # for i, line in enumerate(f):
        #     c = csv.reader(line, dialect=csv.excel_tab)
        #     # x = line.find('\x00')
        #     if i == 23063492:
        #         print(i)
        #         print(repr(line))


if __name__ == "__main__":
    main()