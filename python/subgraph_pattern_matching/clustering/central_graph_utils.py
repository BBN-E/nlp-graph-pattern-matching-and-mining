import operator

import networkx as nx
from ..patterns.pattern import Pattern


# Returns the index of the largest graph in each cluster
def get_biggest_graph_per_cluster(labels, digraph_list):
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


# Returns the index of the most central graph in each cluster
def get_central_graph_per_cluster(labels, distance_matrix):

    cluster_lists = {}

    for i, label in enumerate(labels):
        if label not in cluster_lists:
            cluster_lists[label] = []
        cluster_lists[label].append(i)

    cluster_num_to_central_indexes = {}

    for cluster_num, cluster_list in cluster_lists.items():

        graph_total_distance_tuple_list = []

        for graph_index in cluster_list:

            row = distance_matrix[graph_index]
            total_distance = 0
            for g_index in cluster_list:
                total_distance += row[g_index]

            graph_total_distance_tuple_list.append((graph_index, total_distance))

        graph_total_distance_tuple_list.sort(key=operator.itemgetter(1))

        cluster_num_to_central_indexes[cluster_num] = graph_total_distance_tuple_list[:10]

    return cluster_num_to_central_indexes


# Finds the number of graphs in graph_list isomorphic to each possible subgraph of central_graph
# Used to generalize a pattern that applies to most nodes in a cluster
def find_pattern_for_cluster(central_pattern, pattern_list):

    selected_patterns = []
    central_graph = central_pattern.pattern_graph

    for index, node_set in enumerate(nx.weakly_connected_components(central_graph)):
        subgraph_pattern = central_graph.subgraph(node_set)

        if len(subgraph_pattern.nodes) < 5:
            continue

        num_matches = 0
        for pattern in pattern_list:
            matcher = nx.algorithms.isomorphism.DiGraphMatcher(pattern.pattern_graph, subgraph_pattern,
                                                               pattern.node_match, pattern.edge_match)
            if matcher.subgraph_is_isomorphic():
                num_matches += 1

        if num_matches <= 5:
            continue

        new_pattern = Pattern("selected_pattern_{}_{}".format(index, num_matches), subgraph_pattern,
                              central_pattern._node_attrs, central_pattern._edge_attrs,
                              grid_search=central_pattern.grid_search, category=central_pattern.category)
        selected_patterns.append(new_pattern)

    return selected_patterns