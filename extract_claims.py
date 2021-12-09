import argparse
import networkx as nx

import serifxml3

from graph_builder import GraphBuilder
from digraph_matcher_factory import DiGraphMatcherFactory


def extract_claims(serifxml_path):

    serif_doc = serifxml3.Document(serifxml_path)

    Builder = GraphBuilder()
    document_graph = Builder.convert_serif_doc_to_networkx(serif_doc)
    Builder.visualize_networkx_graph(document_graph)

    Factory = DiGraphMatcherFactory()
    pattern_graph, node_match, edge_match = Factory.ccomp_pattern()

    matcher = nx.algorithms.isomorphism.DiGraphMatcher(document_graph, pattern_graph,
                                                       node_match=node_match,
                                                       edge_match=edge_match)
    subgraph_matches = [g for g in matcher.subgraph_isomorphisms_iter()]
    return subgraph_matches


def main(args):

    matches = extract_claims(args.input)
    print(matches)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str)
    args = parser.parse_args()

    main(args)