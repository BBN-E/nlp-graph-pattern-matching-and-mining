import networkx as nx
import argparse
import json
import os

from view_utils.graph_viewer import GraphViewer
from io_utils.io_utils import deserialize_patterns
import numpy as np

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


def find_pattern_for_cluster(central_pattern, pattern_list):
    # Finds the number of graphs in graph_list isomorphic to each possible subgraph of central_graph
    # Used to generalize a pattern that applies to most nodes in a cluster

    patterns_to_num_matches = {}
    central_graph = central_pattern.pattern_graph

    for node_set in nx.weakly_connected_components(central_graph):
        subgraph_pattern = central_graph.subgraph(node_set)
        # TODO: handle edge and node attributes

        num_matches = 0
        for pattern in pattern_list:
            matcher = nx.algorithms.isomorphism.DiGraphMatcher(pattern.pattern_graph, subgraph_pattern,
                                                               pattern.node_match, pattern.edge_match)
            if matcher.subgraph_is_isomorphic():
                num_matches += 1
        patterns_to_num_matches[subgraph_pattern] = num_matches

    return patterns_to_num_matches


def get_pattern_from_clusters(patterns_list, distance_matrix, labels, output_dir):
    # Find a representative pattern for each cluster of digraphs

    cluster_to_central_graph_index = get_central_graph_per_cluster(labels, distance_matrix)

    graph_viewer = GraphViewer()

    cluster_num_to_cluster_pattern = []

    for cluster_num, graph_index in cluster_to_central_graph_index.items():

        if cluster_num == -1:
            continue

        cur_pattern = patterns_list[graph_index].pattern_graph

        graph_viewer.prepare_mdp_networkx_for_visualization(cur_pattern)

        html_file = os.path.join(output_dir, "central_graph_in_cluster_{}.html".format(cluster_num))

        graph_viewer.visualize_networkx_graph(cur_pattern, html_file=html_file)

        cluster_pattern_list = []
        for i, label in enumerate(labels):
            if label == cluster_num:
                cluster_pattern_list.append(patterns_list[i])

        cluster_pattern = find_pattern_for_cluster(patterns_list[graph_index], cluster_pattern_list)
        cluster_num_to_cluster_pattern.append(cluster_pattern)

    return cluster_num_to_cluster_pattern


def main(args):

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    pattern_list = deserialize_patterns(args.local_patterns_json, is_file_path=True)

    if args.distance_matrix and args.labels:

        with open(args.distance_matrix, 'rb') as f:
            distance_matrix = np.load(f)

        with open(args.labels, 'r') as f:
            labels = json.load(f)

        print(get_pattern_from_clusters(pattern_list, distance_matrix, labels, args.output))
    else:
        for patten in pattern_list:
            graph_viewer = GraphViewer()

            graph_viewer.prepare_mdp_networkx_for_visualization(patten.pattern_graph)
            graph_viewer.prepare_networkx_for_visualization(patten.pattern_graph)
            html_file = os.path.join(args.output, "graph_{}.html".format(patten.pattern_id))
            graph_viewer.visualize_networkx_graph(patten.pattern_graph, html_file=html_file)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--local_patterns_json', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-d', '--distance_matrix', type=str, default=None)
    parser.add_argument('-l', '--labels', type=str, default=None)
    args = parser.parse_args()

    main(args)
