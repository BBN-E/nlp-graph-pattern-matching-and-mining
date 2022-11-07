import csv
from collections import Counter

csv_path = "/nfs/raid83/u13/caml/users/mselvagg_ad/aida-misc/output_csvs/sorted_claims.csv"

counts = Counter()

if __name__ == "__main__":
    with open(csv_path, 'r', newline='\n') as f:
        my_reader = csv.reader(f, delimiter='|')
        for row in my_reader:

            if len(row) != 6:
                continue


            counts[row[0]+row[1]+row[2]] += 1

    print(len(counts))

    # import matplotlib.pyplot as plt
    #
    #
    # plt.bar(counts.keys(), counts.values())
    # plt.xticks(color='w')
    #
    # plt.show()