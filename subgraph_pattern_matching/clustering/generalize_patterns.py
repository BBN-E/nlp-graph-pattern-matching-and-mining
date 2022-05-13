import networkx as nx
import argparse
import json
import os
import operator
import enum
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs

from view_utils.graph_viewer import GraphViewer
from io_utils.io_utils import deserialize_patterns, serialize_patterns
import numpy as np
from patterns.pattern import Pattern
from collections import Counter
from networkx.algorithms import isomorphism


class GeneralizationStrategy(enum.Enum):
    Ungeneralized = enum.auto()
    MajorityWins = enum.auto()


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

    cluster_num_to_central_indexes = {}

    for cluster_num, cluster_list in cluster_lists.items():

        min_distance = float('inf')
        central_graph_index = cluster_list[0]

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


def find_pattern_for_cluster(central_pattern, pattern_list):
    # Finds the number of graphs in graph_list isomorphic to each possible subgraph of central_graph
    # Used to generalize a pattern that applies to most nodes in a cluster

    selected_patterns = []
    central_graph = central_pattern.pattern_graph

    for index, node_set in enumerate(nx.weakly_connected_components(central_graph)):
        subgraph_pattern = central_graph.subgraph(node_set)
        # TODO: handle edge and node attributes

        num_matches = 0
        for pattern in pattern_list:
            matcher = nx.algorithms.isomorphism.DiGraphMatcher(pattern.pattern_graph, subgraph_pattern,
                                                               pattern.node_match, pattern.edge_match)
            if matcher.subgraph_is_isomorphic():
                num_matches += 1

        new_pattern = Pattern("selected_pattern_{}_{}".format(index, num_matches), subgraph_pattern,
                              central_pattern._node_attrs, central_pattern._edge_attrs)
        selected_patterns.append(new_pattern)

    return selected_patterns


def get_pattern_from_clusters(patterns_list, distance_matrix, labels, output_dir):
    # Find a representative pattern for each cluster of digraphs

    cluster_to_central_graph_indexes = get_central_graph_per_cluster(labels, distance_matrix)

    graph_viewer = GraphViewer()

    cluster_num_to_cluster_patterns = [None] * (max(labels) + 1)

    visualizations_dir = os.path.join(output_dir, "visualizations")
    if not os.path.exists(visualizations_dir):
        os.makedirs(visualizations_dir)

    for cluster_num, graph_index_list in cluster_to_central_graph_indexes.items():

        if cluster_num == -1:
            continue

        cluster_pattern_list = []
        for i, label in enumerate(labels):
            if label == cluster_num:
                cluster_pattern_list.append(patterns_list[i])

        cluster_patterns = find_pattern_for_cluster(patterns_list[graph_index_list[0][0]], cluster_pattern_list)
        cluster_num_to_cluster_patterns[cluster_num] = cluster_patterns

        for graph_index, __ in graph_index_list:

            cur_pattern = patterns_list[graph_index].pattern_graph
            graph_viewer.prepare_mdp_networkx_for_visualization(cur_pattern)
            graph_viewer.prepare_amr_networkx_for_visualization(cur_pattern)
            html_file = os.path.join(visualizations_dir, "central_graph_cluster_{}_graph_{}.html".format(cluster_num, graph_index))
            graph_viewer.visualize_networkx_graph(cur_pattern, html_file=html_file)

    return cluster_num_to_cluster_patterns


def add_counts_to_dict(mapping, node_or_edge_list, id_to_attribute_counts):

    for id, attr_dict in node_or_edge_list:
        for attr, value in attr_dict.items():

            if attr not in id_to_attribute_counts[mapping[id]]:
                id_to_attribute_counts[mapping[id]][attr] = {}

            if value not in id_to_attribute_counts[mapping[id]][attr]:
                id_to_attribute_counts[mapping[id]][attr][value] = 0

            id_to_attribute_counts[mapping[id]][attr][value] += 1


def majority_wins_graph(patterns_list, labels, output_dir):

    label_count = Counter(labels)
    generalized_patterns = []

    for pattern_number, label in enumerate(label_count.most_common()):
        if label[1] < 10:
            continue
        most_common_label = label[0]

        # create list of all graphs in the largest cluster
        most_frequent_structure_patterns = []
        for i, label in enumerate(labels):
            if label == most_common_label:
                most_frequent_structure_patterns.append(patterns_list[i])

        # our most frequent pattern
        stripped_graph = nx.convert_node_labels_to_integers(most_frequent_structure_patterns[0].pattern_graph)

        # TODO: come up with way to discard super common graphs
        if len(stripped_graph.nodes) < 5:
            continue

        # maps nodes to dict that maps attributes to dicts of possible values and their counts
        # dict (node, dict ( attr, ( dict (value, count ) ) )
        node_to_attribute_counts = {}
        edge_to_attribute_counts = {}

        # our most frequent pattern, stripped of all node and edge attributes
        for node_id, attr_dict in list(stripped_graph.nodes(data=True)):
            node_to_attribute_counts[node_id] = {}
            node_type = stripped_graph.nodes[node_id][NodeAttrs.node_type]
            stripped_graph.nodes[node_id].clear()
            stripped_graph.nodes[node_id][NodeAttrs.node_type] = node_type
        for node1_id, node2_id, attr_dict in list(stripped_graph.edges(data=True)):
            edge_to_attribute_counts[(node1_id, node2_id)] = {}
            edge_type = stripped_graph.edges[(node1_id, node2_id)][EdgeAttrs.edge_type]
            stripped_graph.edges[(node1_id, node2_id)].clear()
            stripped_graph.edges[(node1_id, node2_id)][EdgeAttrs.edge_type] = edge_type

        # count the frequency of each value of each attribute for each node and edge for each pattern
        for pattern in most_frequent_structure_patterns:
            cur_graph = pattern.pattern_graph

            # create a mapping between each pattern and the abstract structure, to align attr recording
            GM = isomorphism.DiGraphMatcher(cur_graph, stripped_graph, node_match=pattern.node_match, edge_match=pattern.edge_match)
            assert(GM.is_isomorphic())

            mapping = GM.mapping
            add_counts_to_dict(mapping, list(cur_graph.nodes(data=True)), node_to_attribute_counts)

            edge_mapping = {}
            for edge in cur_graph.edges:
                mapped_edge = (mapping[edge[0]], mapping[edge[1]])
                edge_mapping[edge] = mapped_edge
            edge_to_attr_list = []
            for node1_id, node2_id, attr_dict in list(cur_graph.edges(data=True)):
                edge_to_attr_list.append(((node1_id, node2_id), attr_dict))

            add_counts_to_dict(edge_mapping, edge_to_attr_list, edge_to_attribute_counts)

        # set each atrribute of each node and edge to the most frequent value
        all_node_attrs = set()
        attr_tuple_to_count = []

        for node_id, attr_dict in node_to_attribute_counts.items():
            for attr, value_dict in attr_dict.items():
                if attr != NodeAttrs.annotated:
                    all_node_attrs.add(attr)
                most_frequent_value_for_attr = max(value_dict, key=value_dict.get)
                count = value_dict[most_frequent_value_for_attr]

                attr_tuple_to_count.append( (count, "node", node_id, attr, most_frequent_value_for_attr) )

        all_edge_attrs = set()
        for edge_id, attr_dict in edge_to_attribute_counts.items():
            for attr, value_dict in attr_dict.items():
                all_edge_attrs.add(attr)
                most_frequent_value_for_attr = max(value_dict, key=value_dict.get)
                count = value_dict[most_frequent_value_for_attr]
                attr_tuple_to_count.append((count, "edge", edge_id, attr, most_frequent_value_for_attr))

        # only add the most common attribute, value pairs
        attr_tuple_to_count.sort(key=operator.itemgetter(0), reverse=True)
        for count, type, id, attr, value in attr_tuple_to_count:
            if count < len(most_frequent_structure_patterns) * 0.66:
                break

            if type == "node":
                stripped_graph.nodes[id][attr] = value
            elif type == "edge":
                stripped_graph.edges[id][attr] = value

        grid_search = patterns_list[0].grid_search
        category = patterns_list[0].category
        gen_pattern = Pattern('majority_wins_' + grid_search + "_" + str(pattern_number), stripped_graph, list(all_node_attrs), list(all_edge_attrs), grid_search=grid_search, category=category)
        generalized_patterns.append(gen_pattern)

    return [generalized_patterns]


def majority_wins_strategy(args, pattern_list, graph_viewer, visualizations_dir):

    assert(args.labels)

    with open(args.labels, 'r') as f:
        labels = json.load(f)

    cluster_num_to_cluster_patterns = majority_wins_graph(pattern_list, labels, args.output)

    for cluster_num, cluster_patterns in enumerate(cluster_num_to_cluster_patterns):
        json_dump = serialize_patterns(cluster_patterns)

        with open(os.path.join(args.output, "patterns_cluster_{}.json".format(cluster_num)), 'w') as f:
            f.write(json_dump)

        for i, cluster_pattern in enumerate(cluster_patterns):
            graph_viewer.prepare_mdp_networkx_for_visualization(cluster_pattern.pattern_graph)
            graph_viewer.prepare_amr_networkx_for_visualization(cluster_pattern.pattern_graph)
            html_file = os.path.join(visualizations_dir, "majority_graph_{}.html".format(i))
            graph_viewer.visualize_networkx_graph(cluster_pattern.pattern_graph, html_file=html_file)


def ungeneralized_strategy(args, pattern_list):
    json_dump = serialize_patterns(pattern_list)
    with open(os.path.join(args.output, "patterns_cluster_0.json"), 'w') as f:
        f.write(json_dump)


def main(args):
    graph_viewer = GraphViewer()
    visualizations_dir = os.path.join(args.output, "visualizations")
    if not os.path.exists(visualizations_dir):
        os.makedirs(visualizations_dir)

    pattern_list = deserialize_patterns(args.local_patterns_json, is_file_path=True)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if GeneralizationStrategy[args.strategy] == GeneralizationStrategy.MajorityWins:
        majority_wins_strategy(args, pattern_list, graph_viewer, visualizations_dir)
    elif GeneralizationStrategy[args.strategy] == GeneralizationStrategy.Ungeneralized:
        ungeneralized_strategy(args, pattern_list)
    else:
        raise NotImplementedError("Generalization strategy {} not implemented".format(args.strategy))

    examples_dir = os.path.join(visualizations_dir, "examples")
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)

    # Get 100 sample graphs to use as visualizations
    for i, pattern in enumerate(pattern_list[0::10]):
        graph_viewer.prepare_amr_networkx_for_visualization(pattern.pattern_graph)
        graph_viewer.prepare_mdp_networkx_for_visualization(pattern.pattern_graph)
        html_file = os.path.join(examples_dir, "graph_{}.html".format(pattern.pattern_id))
        graph_viewer.visualize_networkx_graph(pattern.pattern_graph, html_file=html_file)
        if i > 100:
            break


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--local_patterns_json', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-s', '--strategy', type=str, required=True)
    parser.add_argument('-d', '--distance_matrix', type=str, default=None)
    parser.add_argument('-l', '--labels', type=str, default=None)
    args = parser.parse_args()

    main(args)
