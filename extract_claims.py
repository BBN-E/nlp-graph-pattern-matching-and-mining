import os, json
import argparse
import networkx as nx
from collections import defaultdict

import serifxml3

from graph_builder import GraphBuilder
from digraph_matcher_factory import DiGraphMatcherFactory
from match_wrapper import MatchWrapper, MatchCorpus


def extract_claims(serifxml_path, visualize=False):

    print(serifxml_path)
    serif_doc = serifxml3.Document(serifxml_path)

    GB = GraphBuilder()
    document_graph = GB.convert_serif_doc_to_networkx(serif_doc)
    if visualize:
        GB.visualize_networkx_graph(document_graph)

    Factory = DiGraphMatcherFactory()

    matches = []
    for pattern_id, pattern in Factory.basic_patterns.items():

        pattern_graph, node_match, edge_match = pattern()

        pattern_matcher = nx.algorithms.isomorphism.DiGraphMatcher(document_graph, pattern_graph,
                                                                   node_match=node_match,
                                                                   edge_match=edge_match)
        pattern_match_dicts = [g for g in pattern_matcher.subgraph_isomorphisms_iter()]

        # TODO create on-match-filter API that is not ad-hoc
        ###########################################################################################################
        if pattern_id == 'relaxed_ccomp':
            from on_match_filters import is_ancestor
            pattern_match_dicts = [m for m in pattern_match_dicts if is_ancestor(match_node_id_to_pattern_node_id=m, document_graph=document_graph,
                                                                                 ancestor_id='CCOMP_TOKEN', descendant_id='EVENT_TOKEN')]
        ###########################################################################################################

        pattern_match_dicts = list(map(dict, set(tuple(sorted(m.items())) for m in pattern_match_dicts)))  # deduplicate (sanity check)
        pattern_matches = [MatchWrapper(m, pattern_id, serif_doc) for m in pattern_match_dicts]

        matches.extend(pattern_matches)

    return matches


def main(args):

    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    all_matches = []
    for serifxml_path in serifxml_paths:
        all_matches.extend(extract_claims(serifxml_path, visualize=args.visualize))

    match_corpus = MatchCorpus(all_matches)
    match_corpus.extraction_stats()
    match_corpus.count_intersentence_conceiver_event_edges()

    # ccomp_family_random_sample = match_corpus.random_sample({'ccomp', 'relaxed_ccomp', 'relaxed_ccomp_one_hop'}, sample_size=10)
    # according_to_random_sample = match_corpus.random_sample({'according_to'}, sample_size=10)
    #
    # for m in ccomp_family_random_sample:
    #     print(m)
    # print("\n\n====================\n====================\n\n")
    # for m in according_to_random_sample:
    #     print(m)


if __name__ == '__main__':
    '''
    PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python
    python3 \
    /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/extract_claims.py \
    -i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/lists/modal.serifxml.test \
    -l
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-v', '--visualize', action='store_true')
    # parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    main(args)