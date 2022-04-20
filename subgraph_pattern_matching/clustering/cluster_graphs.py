import argparse
import json
import enum
import numpy as np
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from io_utils.io_utils import deserialize_pattern_graphs


class ClusterOptions(enum.Enum):
    DBSCAN = enum.auto()


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


def main(args):
    digraph_list = deserialize_pattern_graphs(args.digraphs_json, is_file_path=True)

    with open(args.distance_matrix, 'rb') as f:
        distance_matrix = np.load(f)

    labels = cluster_digraphs(digraph_list, distance_matrix, ClusterOptions[args.cluster_option])

    with open(args.output, 'w') as f:
        json.dump(labels.tolist(), f, indent=4)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--digraphs_json', type=str, required=True)
    parser.add_argument('-d', '--distance_matrix', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-c', '--cluster_option', type=str, default="DBSCAN")
    args = parser.parse_args()

    main(args)

