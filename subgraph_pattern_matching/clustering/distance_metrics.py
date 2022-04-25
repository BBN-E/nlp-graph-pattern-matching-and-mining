import numpy as np

from networkx.algorithms.similarity import optimize_graph_edit_distance


def approximate_graph_edit_distance(G1, G2):

    return next(optimize_graph_edit_distance(G1.pattern_graph, G2.pattern_graph, G1.node_match, G1.edge_match))


def normalized_graph_edit_distance(G1, G2):

    edit_distance = next(optimize_graph_edit_distance(G1.pattern_graph, G2.pattern_graph, G1.node_match, G1.edge_match))

    return edit_distance / (len(G1)+len(G2))


def create_distance_matrix(local_patterns, similarity_measure, stripe=0, num_batches=1):
    '''

    :param local_patterns: list[networkx.classes.digraph.DiGraph]
    :param similarity_measure: function that returns float similarity score between two digraphs

    :return: distance_matrix: 2D ndarray
    '''

    row_size = len(local_patterns)
    print("Total length: {}".format(row_size))

    distance_matrix = np.empty((row_size, row_size), float)

    for i, pattern_i in enumerate(local_patterns):
        for j, pattern_j in (enumerate(local_patterns[i:], i)):

            if ((i * row_size + j) % num_batches) == stripe:

                sim_score = similarity_measure(pattern_i, pattern_j)
                # print("{}, {}: {}".format(i, j, sim_score))
                distance_matrix[i][j] = sim_score

                if i != j:
                    distance_matrix[j][i] = distance_matrix[i][j]

    return distance_matrix