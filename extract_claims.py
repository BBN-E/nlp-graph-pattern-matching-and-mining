import os, json
import argparse
import networkx as nx
from collections import defaultdict

import serifxml3

from graph_builder import GraphBuilder
from digraph_matcher_factory import DiGraphMatcherFactory


def extract_claims(serifxml_path, all_matches, stats, visualize=False):

    print(serifxml_path)
    serif_doc = serifxml3.Document(serifxml_path)

    GB = GraphBuilder()
    document_graph = GB.convert_serif_doc_to_networkx(serif_doc)
    if visualize:
        GB.visualize_networkx_graph(document_graph)

    Factory = DiGraphMatcherFactory()

    for pattern_id, pattern in Factory.patterns.items():

        pattern_graph, node_match, edge_match = pattern()

        matcher = nx.algorithms.isomorphism.DiGraphMatcher(document_graph, pattern_graph,
                                                           node_match=node_match,
                                                           edge_match=edge_match)
        matches = [g for g in matcher.subgraph_isomorphisms_iter()]

        # TODO create on-match-filter API that is not ad-hoc
        ###########################################################################################################
        if pattern_id == 'relaxed_ccomp':
            from on_match_filters import is_ancestor
            matches = [m for m in matches if is_ancestor(isomorphism_dict=m, document_graph=document_graph,
                                                         ancestor_id='CCOMP_TOKEN', descendant_id='EVENT_TOKEN')]
        ###########################################################################################################
        # for i,m in enumerate(matches):
        #     print(pattern_id, '\t', i, '\t', m)

        matches = list(map(dict, set(tuple(sorted(m.items())) for m in matches)))  # deduplicate (sanity check)

        all_matches[pattern_id].extend(matches)
        stats[pattern_id] += len(matches)

    return all_matches, stats


def main(args):

    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    stats = defaultdict(int)
    all_matches = defaultdict(list)
    for serifxml_path in serifxml_paths:
        all_matches, stats = extract_claims(serifxml_path, all_matches=all_matches, stats=stats, visualize=args.visualize)

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(all_matches, f, sort_keys=True, indent=4)

    print(stats)

if __name__ == '__main__':

    # PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python/ python3 /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/extract_claims.py -i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml/reuters_3003584698.xml

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-v', '--visualize', action='store_true')
    parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    main(args)