import networkx as nx
import argparse
import json
import os
import operator
import enum

import numpy as np
from collections import Counter
from networkx.algorithms import isomorphism

from utils.io_utils import deserialize_patterns, serialize_patterns
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.node.node_attrs import NodeAttrs
from patterns.pattern import Pattern
from view_utils.graph_viewer import GraphViewer
from graph_builder import GraphBuilder

class GeneralizationStrategy(enum.Enum):
    Ungeneralized = enum.auto()
    CentralGraph = enum.auto()
    MajorityWins = enum.auto()
    GSpan = enum.auto()
    SPMiner = enum.auto()

def central_graph_strategy(patterns_list, distance_matrix_path, labels_path):
    from clustering.central_graph_utils import get_central_graph_per_cluster, find_pattern_for_cluster

    with open(distance_matrix_path, 'rb') as f:
        distance_matrix = np.load(f)

    with open(labels_path, 'r') as f:
        labels = json.load(f)

    # Find a representative graph for each cluster of digraphs
    cluster_to_central_graph_indexes = get_central_graph_per_cluster(labels, distance_matrix)
    cluster_num_to_cluster_patterns = [None] * (max(labels) + 1)

    for cluster_num, graph_index_list in cluster_to_central_graph_indexes.items():

        if cluster_num == -1:
            continue

        cluster_pattern_list = []
        for i, label in enumerate(labels):
            if label == cluster_num:
                cluster_pattern_list.append(patterns_list[i])

        cluster_patterns = find_pattern_for_cluster(patterns_list[graph_index_list[0][0]], cluster_pattern_list)
        cluster_num_to_cluster_patterns[cluster_num] = cluster_patterns

    return cluster_num_to_cluster_patterns


# helper function for majority wins graph
def add_counts_to_dict(mapping, node_or_edge_list, id_to_attribute_counts):

    for id, attr_dict in node_or_edge_list:
        for attr, value in attr_dict.items():

            if attr not in id_to_attribute_counts[mapping[id]]:
                id_to_attribute_counts[mapping[id]][attr] = {}

            if value not in id_to_attribute_counts[mapping[id]][attr]:
                id_to_attribute_counts[mapping[id]][attr][value] = 0

            id_to_attribute_counts[mapping[id]][attr][value] += 1


# main logic of majority wins strategy
def majority_wins_strategy(patterns_list, labels_path):

    with open(labels_path, 'r') as f:
        labels = json.load(f)

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

        if len(stripped_graph.edges) <= 1:
            continue

        grid_search = patterns_list[0].grid_search
        category = patterns_list[0].category
        gen_pattern = Pattern('majority_wins_' + grid_search + "_" + str(pattern_number), stripped_graph,
                              list(all_node_attrs), list(all_edge_attrs), grid_search=grid_search, category=category)
        generalized_patterns.append(gen_pattern)

    return [generalized_patterns]


def gspan_strategy(args, pattern_list):
    from gspan_mining.gspan import gSpan

    grid_search = pattern_list[0].grid_search
    category = pattern_list[0].category

    gb = GraphBuilder()
    gv = GraphViewer()

    gs = gSpan(min_support=args.min_support,
               min_num_vertices=args.min_num_vertices,
               max_num_vertices=args.max_num_vertices,
               is_undirected=False, where=False)
    gs.expanded = True

    expanded_graphs = [GraphBuilder.expand_graph(pattern.pattern_graph) for pattern in pattern_list]

    gs._read_graphs_from_networkx(expanded_graphs)
    gs.run()

    visualizations_dir = os.path.join(args.output, "visualizations", "gspan_patterns")
    os.makedirs(visualizations_dir, exist_ok=True)

    gspan_pattern_list = []
    for j, fs in enumerate(gs.frequent_subgraphs):
        G = gb.gspan_graph_to_networkx(fs.graph,
                                       node_labels=fs.node_labels,
                                       edge_labels=fs.edge_labels)

        os.makedirs(visualizations_dir + "/" + str(j), exist_ok=True)

        for support_id in fs.support:
            support_G = gs.graphs[support_id]
            support_g_networkx = gb.gspan_graph_to_networkx(support_G,
                                        node_labels=gs.node_labels,
                                        edge_labels=gs.edge_labels)
            html_file = os.path.join(visualizations_dir, str(j), f"pattern_{support_G.gid}.html")
            gv.prepare_networkx_for_visualization(support_g_networkx)
            gv.visualize_networkx_graph(support_g_networkx, html_file, sentence_text=str(support_G.gid))

        P = Pattern(f"gSpan_{j}", GraphBuilder.compress_graph(G),
                    [NodeAttrs.node_type],
                    [EdgeAttrs.edge_type],
                    grid_search=grid_search,
                    category=category)
        gspan_pattern_list.append(P)
        html_file = os.path.join(visualizations_dir, str(j), f"generalized_pattern_{fs.gid}.html")
        text = f"There are {len(fs.support)} supporting instances for this pattern"
        gv.prepare_networkx_for_visualization(G)
        gv.visualize_networkx_graph(G, html_file, sentence_text=text)

    return [gspan_pattern_list]

def spminer_strategy(args, pattern_list):
    from subgraph_mining.decoder import pattern_growth
    from subgraph_mining.config import parse_decoder
    from subgraph_matching.config import parse_encoder

    pattern_kwargs = {'node_attrs': pattern_list[0]._node_attrs, 'edge_attrs': pattern_list[0]._edge_attrs,
                      'grid_search': pattern_list[0].grid_search, 'category': pattern_list[0].category}

    expanded_graphs = [GraphBuilder.expand_graph(pattern.pattern_graph, digraph=False) for pattern in pattern_list]
    node_v2n, node_n2v, edge_v2n, edge_n2v = GraphBuilder.numerize_attribute_values(graphs=expanded_graphs)

    dataset = GraphBuilder.numerize_graphs(graphs=expanded_graphs, node_v2n=node_v2n, edge_v2n=edge_v2n)

    parser = argparse.ArgumentParser()
    parse_encoder(parser)
    parse_decoder(parser)
    spminer_args = parser.parse_args("")

    plots_dir = os.path.join(args.output, "plots/cluster")
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)

    with open(args.spminer_config, 'r') as f:
        spminer_config = json.load(f)

    argparse_dict = vars(spminer_args)
    argparse_dict.update(spminer_config)
    argparse_dict['plots_dir'] = plots_dir
    argparse_dict['out_path'] = os.path.join(args.output, "results.pkl")

    out_graphs = pattern_growth(dataset, 'graph', spminer_args)

    denumerized_graphs = GraphBuilder.denumerize_graphs(out_graphs, node_n2v=node_n2v, edge_n2v=edge_n2v)
    generalized_patterns = []
    for i, pattern_graph in enumerate(denumerized_graphs):
        pattern = Pattern(pattern_id=i, pattern_graph=GraphBuilder.compress_graph(pattern_graph), **pattern_kwargs)
        generalized_patterns.append(pattern)

    return [generalized_patterns]


def main(args):
    graph_viewer = GraphViewer()
    visualizations_dir = os.path.join(args.output, "visualizations")
    if not os.path.exists(visualizations_dir):
        os.makedirs(visualizations_dir)

    pattern_list = deserialize_patterns(args.local_patterns_json, is_file_path=True)

    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    if GeneralizationStrategy[args.strategy] == GeneralizationStrategy.MajorityWins:
        generalized_patterns_lists = majority_wins_strategy(pattern_list, args.labels)
    elif GeneralizationStrategy[args.strategy] == GeneralizationStrategy.Ungeneralized:
        generalized_patterns_lists = [pattern_list]
    elif GeneralizationStrategy[args.strategy] == GeneralizationStrategy.GSpan:
        generalized_patterns_lists = gspan_strategy(args, pattern_list)
    elif GeneralizationStrategy[args.strategy] == GeneralizationStrategy.CentralGraph:
        generalized_patterns_lists = central_graph_strategy(pattern_list, args.distance_matrix, args.labels)
    elif GeneralizationStrategy[args.strategy] == GeneralizationStrategy.SPMiner:
        generalized_patterns_lists = spminer_strategy(args, pattern_list)
    else:
        raise NotImplementedError("Generalization strategy {} not implemented".format(args.strategy))

    for cluster_num, generalized_patterns_list in enumerate(generalized_patterns_lists):

        json_dump = serialize_patterns(generalized_patterns_list)
        with open(os.path.join(args.output, "patterns_cluster_{}.json".format(cluster_num)), 'w') as f:
            f.write(json_dump)

        if GeneralizationStrategy[args.strategy] == GeneralizationStrategy.MajorityWins:
            for i, pattern in enumerate(generalized_patterns_list):
                html_file = os.path.join(visualizations_dir, "pattern_graph_{}_{}.html".format(cluster_num, i))
                graph_viewer.prepare_networkx_for_visualization(pattern.pattern_graph)
                graph_viewer.visualize_networkx_graph(pattern.pattern_graph, html_file=html_file)


    examples_dir = os.path.join(visualizations_dir, "examples")
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)

    # Get 100 sample graphs to use as visualizations
    for i, pattern in enumerate(pattern_list[0::10]):
        html_file = os.path.join(examples_dir, "graph_{}.html".format(pattern.pattern_id))
        graph_viewer.prepare_networkx_for_visualization(pattern.pattern_graph)
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
    parser.add_argument('--min_support', type=int, default=40, help="Minimum number of supporting graphs for gspan")
    parser.add_argument('--min_num_vertices', type=int, default=7, help="Minimum number of vertices in gspan pattern")
    parser.add_argument('--max_num_vertices', type=float, default=float('inf'), help="Maximum number of vertices in gspan pattern")
    parser.add_argument('--spminer_config', type=str, default=None, help="Path to config json for SPMiner")

    args = parser.parse_args()

    main(args)
