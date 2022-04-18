from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import enum
import numpy as np
import argparse
import networkx as nx
from pattern_factory import deserialize_pattern_graphs
from view_utils.graph_viewer import GraphViewer
from kneed import KneeLocator


class ClusterOptions(enum.Enum):
    DBSCAN = enum.auto()


def get_biggest_graph_per_cluster(labels, digraph_list):
    # Returns the index of the largest graph in each cluster
    cluster_lists = {}

    for i, label in enumerate(labels):
        if label not in cluster_lists:
            cluster_lists[label] = []
        cluster_lists[label].append(i)

    cluster_num_to_largest_graph_index = {}

    for cluster_num, cluster_list in cluster_lists.items():

        largest_graph_index = 0
        largest_graph_size = -1
        for graph_index in cluster_list:
            if len(digraph_list[graph_index]) > largest_graph_size:
                largest_graph_index = graph_index
                largest_graph_size = len(digraph_list[graph_index])

        cluster_num_to_largest_graph_index[cluster_num] = largest_graph_index

    return cluster_num_to_largest_graph_index


def get_central_graph_per_cluster(labels, distance_matrix):
    # Returns the index of the most central graph in each cluster

    cluster_lists = {}

    for i, label in enumerate(labels):
        if label not in cluster_lists:
            cluster_lists[label] = []
        cluster_lists[label].append(i)

    cluster_num_to_central_index = {}

    for cluster_num, cluster_list in cluster_lists.items():

        min_distance = float('inf')
        central_graph_index = cluster_list[0]

        for graph_index in cluster_list:

            row = distance_matrix[graph_index]

            total_distance = 0
            for g_index in cluster_list:
                total_distance += row[g_index]

            if total_distance < min_distance:
                central_graph_index = graph_index
                min_distance = total_distance

        cluster_num_to_central_index[cluster_num] = central_graph_index

    return cluster_num_to_central_index


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


def find_pattern_for_cluster(central_graph, graph_list):
    # Finds the number of graphs in graph_list isomorphic to each possible subgraph of central_graph
    # Used to generalize a pattern that applies to most nodes in a cluster

    patterns_to_num_matches = {}

    for node_set in nx.weakly_connected_components(central_graph):
        subgraph_pattern = central_graph.subgraph(node_set)
        # TODO: handle edge and node attributes

        num_matches = 0
        for graph in graph_list:
            matcher = nx.algorithms.isomorphism.DiGraphMatcher(graph, subgraph_pattern)
            # TODO: runtime bad -- research non NP-complete way to approximate?
            if matcher.subgraph_is_isomorphic():
                num_matches += 1
        patterns_to_num_matches[subgraph_pattern] = num_matches

    return patterns_to_num_matches


def cluster_digraphs(digraphs_list, distance_matrix, cluster_option=ClusterOptions.DBSCAN):

    if cluster_option == ClusterOptions.DBSCAN:
        labels = dbscan_cluster(distance_matrix)
    else:
        raise NotImplementedError("Cluster method {} not implemented".format(cluster_option))

    cluster_to_central_graph_index = get_central_graph_per_cluster(labels, distance_matrix)

    graph_viewer = GraphViewer()

    for cluster_num, graph_index in cluster_to_central_graph_index.items():

        graph_viewer.prepare_mdp_networkx_for_visualization(digraphs_list[graph_index])
        graph_viewer.prepare_networkx_for_visualization(digraphs_list[graph_index])

        graph_viewer.visualize_networkx_graph(digraphs_list[graph_index], html_file="central_graph_in_cluster_{}.html".format(cluster_num))

        # TODO: do this for each cluster properly
        print(find_pattern_for_cluster(digraphs_list[graph_index], digraphs_list))

    return labels


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--digraphs_json', type=str, required=True)
    parser.add_argument('-l', '--distance_matrix', type=str, required=True)
    parser.add_argument('-c', '--cluster_option', type=str, default="DBSCAN")
    args = parser.parse_args()

    digraph_list = deserialize_pattern_graphs(args.digraphs_json, is_file_path=True)

    with open(args.distance_matrix, 'rb') as f:
        distance_matrix = np.load(f)
        print(distance_matrix)

    cluster_digraphs(digraph_list, distance_matrix, ClusterOptions[args.cluster_option])

    # from os import listdir
    #
    # distance_matrices = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/run_jobs/expts/4-18-2022-aida-digraphs/combined_matrices"
    #
    # for f in listdir():
    #     diagraph_list = deserialize_pattern_graphs(, is_file_path=True)


