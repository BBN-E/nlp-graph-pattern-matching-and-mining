import argparse
import networkx as nx

import serifxml3

from graph_builder import GraphBuilder
from digraph_matcher_factory import DiGraphMatcherFactory


def extract_claims(serifxml_path, visualize=False):

    serif_doc = serifxml3.Document(serifxml_path)

    GB = GraphBuilder()
    document_graph = GB.convert_serif_doc_to_networkx(serif_doc)
    if visualize:
        GB.visualize_networkx_graph(document_graph)

    Factory = DiGraphMatcherFactory()

    all_matches = dict()
    for pattern_id, pattern in Factory.patterns.items():

        pattern_graph, node_match, edge_match = pattern()

        matcher = nx.algorithms.isomorphism.DiGraphMatcher(document_graph, pattern_graph,
                                                           node_match=node_match,
                                                           edge_match=edge_match)
        matches = [g for g in matcher.subgraph_isomorphisms_iter()]
        for i,m in enumerate(matches):
            print(pattern_id, '\t', i, '\t', m)
        all_matches[pattern_id] = matches

    return all_matches


def main(args):

    matches = extract_claims(args.input, visualize=args.visualize)


if __name__ == '__main__':

    # PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python/ python3 /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/extract_claims.py -i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml/reuters_3003584698.xml

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-v', '--visualize', action='store_true')
    args = parser.parse_args()

    main(args)