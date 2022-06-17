
from utils.io_utils import split_by_config
import argparse

def main(args):
    split_by_config(args.input_patterns, args.output_dir)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_patterns', type=str, required=True)
    parser.add_argument('-o', '--output_dir', type=str, required=True)
    args = parser.parse_args()
    main(args)
