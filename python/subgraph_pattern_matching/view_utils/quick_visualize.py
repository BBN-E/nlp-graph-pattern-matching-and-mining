import argparse
import os

import networkx as nx
from ..local_pattern_finder import ParseTypes
from ..utils.io_utils import deserialize_patterns
from ..view_utils.graph_viewer import GraphViewer


def visualize_patterns_from_list(generalized_patterns, visualization_dir):


    generalized_patterns_list = deserialize_patterns(generalized_patterns, is_file_path=True)
    GV = GraphViewer()
    for i, pattern in enumerate(generalized_patterns_list[:50]):
        graph = nx.convert_node_labels_to_integers(pattern.pattern_graph)

        GV.prepare_networkx_for_visualization(graph)
        parse_types = pattern.grid_search.split("_")[2].split("-")

        corrected_parse_types = "-".join([ParseTypes(int(p)).name for p in parse_types])

        html_file = os.path.join(visualization_dir, "pattern_graph_{}_{}.html".format(corrected_parse_types, pattern.pattern_id))
        GV.visualize_networkx_graph(graph, html_file=html_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--generalized_patterns', type=str, required=True)
    parser.add_argument('-v', '--visualization_dir', type=str, required=True)
    args = parser.parse_args()

    visualize_patterns_from_list(args.generalized_patterns, args.visualization_dir)

# PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching  python3 /nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching/view_utils/quick_visualize.py
