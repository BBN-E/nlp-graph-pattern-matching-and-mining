import numpy as np
import argparse
import os

def combine_distance_matrices(distance_matrices, num_batches):
    row_len = distance_matrices[0].shape[0]

    combined_distance_matrix = np.empty((row_len, row_len), float)
    for i in range(row_len):
        for j in range(i, row_len):
            batch_num = (i * row_len + j) % num_batches
            combined_distance_matrix[i][j] = distance_matrices[batch_num][i][j]
            if j != i:
                combined_distance_matrix[j][i] = combined_distance_matrix[i][j]

    return combined_distance_matrix

def main(args):

    distance_matrices = []
    for index in range(args.num_batches):
        with open(os.path.join(args.input_dir_path, "dist_matrix_split_{}".format(index)), 'rb') as f:
            dist_matrix = np.load(f)
            distance_matrices.append(dist_matrix)

    combined_distance_matrix = combine_distance_matrices(distance_matrices, args.num_batches)

    with open(args.output_file_path, 'wb') as f:
        np.save(f, combined_distance_matrix)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--num_batches', type=int, required=True)
    parser.add_argument('--input_dir_path', type=str, required=True)
    parser.add_argument('--output_file_path', type=str, required=True)
    args = parser.parse_args()

    main(args)
