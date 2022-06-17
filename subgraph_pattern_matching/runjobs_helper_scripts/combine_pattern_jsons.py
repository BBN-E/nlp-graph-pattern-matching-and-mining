import argparse
from utils.io_utils import combine_pattern_lists


def main(args):
    file_paths = []
    with open(args.input_list, 'r') as f:
        for path in f.readlines():
            file_paths.append(path.strip())

    json_dump = combine_pattern_lists(file_paths)

    with open(args.output, 'w') as out_f:
        out_f.write(json_dump)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_list', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    args = parser.parse_args()

    main(args)


