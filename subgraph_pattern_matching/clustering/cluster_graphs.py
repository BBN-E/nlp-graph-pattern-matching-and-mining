import argparse
import json
import enum
import numpy as np
from kneed import KneeLocator
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors


class ClusterOptions(enum.Enum):
    DBSCAN = enum.auto()
    IdenticalStructures = enum.auto()


def group_identical_structures(distance_matrix):

    clusters = []
    labeled_indices = set()

    for i, row in enumerate(distance_matrix):
        if i in labeled_indices:
            continue

        cur_cluster = set()
        for j, dist in enumerate(row):
            if dist == 0:
                cur_cluster.add(j)

        clusters.append(cur_cluster)
        labeled_indices |= cur_cluster

    labels = [-1] * distance_matrix.shape[0]
    for cluster_num, cluster_set in enumerate(clusters):
        for i in list(cluster_set):
            labels[i] = cluster_num

    return labels

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

    epsilon = kneedle.knee_y
    if epsilon <= 0:
        epsilon = 5

    clustering = DBSCAN(eps=epsilon, min_samples=5, metric="precomputed")
    clustering.fit(distance_matrix)

    core_samples_mask = np.zeros_like(clustering.labels_, dtype=bool)
    core_samples_mask[clustering.core_sample_indices_] = True
    labels = clustering.labels_

    # Number of clusters in labels, ignoring noise if present
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print("Estimated number of clusters: {}".format(n_clusters))
    print("Estimated number of noise points: {}".format(n_noise))

    return labels.tolist()


def cluster_patterns(distance_matrix, cluster_option=ClusterOptions.DBSCAN):

    if cluster_option == ClusterOptions.DBSCAN:
        labels = dbscan_cluster(distance_matrix)
    elif cluster_option == ClusterOptions.IdenticalStructures:
        labels = group_identical_structures(distance_matrix)
    else:
        raise NotImplementedError("Cluster method {} not implemented".format(cluster_option))

    return labels


def main(args):

    with open(args.distance_matrix, 'rb') as f:
        distance_matrix = np.load(f)

    labels = cluster_patterns(distance_matrix, ClusterOptions[args.cluster_option])

    with open(args.output, 'w') as f:
        json.dump(labels, f, indent=4)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--distance_matrix', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-c', '--cluster_option', type=str, default="DBSCAN")
    args = parser.parse_args()

    main(args)

