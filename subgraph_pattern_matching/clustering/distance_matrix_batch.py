import json
import numpy as np
import argparse

from networkx.readwrite import json_graph

from distance_metrics import approximate_graph_edit_distance, create_distance_matrix


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stripe', type=int, required=True)
    parser.add_argument('--num_batches', type=int, required=True)
    parser.add_argument('--output_file_path', type=str, required=True)
    parser.add_argument('--input_graphs', type=str, required=True)
    args = parser.parse_args()

    with open(args.input_graphs, 'r') as f:
        node_link_data_list = json.load(f)

    digraph_list = []
    for node_link_data in node_link_data_list:
        digraph = json_graph.node_link_graph(node_link_data)
        digraph_list.append(digraph)

    local_patterns = digraph_list
    distance_matrix = create_distance_matrix(local_patterns, approximate_graph_edit_distance,
                                             stripe=args.stripe, num_batches=args.num_batches)

    with open(args.output_file_path, 'wb') as f:
        np.save(f, distance_matrix)


