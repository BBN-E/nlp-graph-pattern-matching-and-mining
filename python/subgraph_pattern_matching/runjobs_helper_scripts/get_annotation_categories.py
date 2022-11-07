import argparse

from ..local_pattern_finder import read_corpus


def main(args):

    corpus = read_corpus(args.annotation_corpus)

    categories = corpus.get_categories()

    with open(args.output, 'w') as f:
        for cat in categories:
            f.write(cat + "\n")

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annotation_corpus', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()
    main(args)
