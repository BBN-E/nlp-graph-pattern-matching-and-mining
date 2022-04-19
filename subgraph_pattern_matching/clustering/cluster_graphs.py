import argparse

import os
import json
import enum
import numpy as np
import networkx as nx
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from pattern_factory import deserialize_pattern_graphs


class ClusterOptions(enum.Enum):
    DBSCAN = enum.auto()


def main(args):

    distance_matrices = {}
    config_to_annotation_subgraphs = {}

    # load distance matrices and saved digraphs
    with open(args.index_to_config_json_path) as index_to_config_f:
        index_to_config_key = json.load(index_to_config_f)

    for index, key in index_to_config_key.items():
        digraph_path = os.path.join(args.digraph_dir, "digraphs_{}.json".format(index))
        digraph_list = deserialize_pattern_graphs(digraph_path, is_file_path=True)
        config_to_annotation_subgraphs[key] = digraph_list

        distance_matrix_path = os.path.join(args.distance_matrices_dir,
                                            "combined_distance_matrix_digraphs_{}.json.np".format(index))
        with open(distance_matrix_path, 'rb') as f:
            distance_matrix = np.load(f)
            distance_matrices[key] = distance_matrix

    key_to_labels = {}
    # cluster local patterns on train set, create representative pattern from each cluster
    for key, distance_matrix in distance_matrices.items():
        print(key)
        labels = cluster_digraphs(config_to_annotation_subgraphs[key], distance_matrix, ClusterOptions[args.cluster_option])
        key_to_labels[key] = labels

    return key_to_labels


def dbscan_cluster(distance_matrix):

    # Finds elbow point of NearestNeighbors graph to find optimal epsilon value
    neigh = NearestNeighbors(n_neighbors=2, metric="precomputed")
    nbrs = neigh.fit(distance_matrix)
    distances, indices = nbrs.kneighbors(distance_matrix)
    distances = np.sort(distances, axis=0)
    distances = distances[:, 1]
    kneedle = KneeLocator([i for i in range(len(distances))], distances, S=1.0, curve="convex", direction="increasing")
    # kneedle.plot_knee()
    # plt.show()

    clustering = DBSCAN(eps=kneedle.knee_y, min_samples=5, metric="precomputed")
    clustering.fit(distance_matrix)

    core_samples_mask = np.zeros_like(clustering.labels_, dtype=bool)
    core_samples_mask[clustering.core_sample_indices_] = True
    labels = clustering.labels_

    # Number of clusters in labels, ignoring noise if present
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print("Estimated number of clusters: {}".format(n_clusters))
    print("Estimated number of noise points: {}".format(n_noise))

    return labels


def cluster_digraphs(digraphs_list, distance_matrix, cluster_option=ClusterOptions.DBSCAN):

    if cluster_option == ClusterOptions.DBSCAN:
        labels = dbscan_cluster(distance_matrix)
    else:
        raise NotImplementedError("Cluster method {} not implemented".format(cluster_option))

    return labels


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--digraphs_dir', type=str, required=True)
    parser.add_argument('-d', '--distance_matrice_dir', type=str, required=True)
    parser.add_argument('-i', '--index_to_config_json_path', type=str, required=True)
    parser.add_argument('-c', '--cluster_option', type=str, default="DBSCAN")
    args = parser.parse_args()

    main(args)

