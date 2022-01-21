import os, json
import argparse
import logging
import networkx as nx
from collections import defaultdict

import serifxml3

from graph_builder import GraphBuilder
from pattern_factory import PatternFactory
from match_wrapper import MatchWrapper, MatchCorpus
from constants import PatternTokenNodeIDs

from timer import timer


logging.basicConfig(level=logging.INFO)


@timer
def prepare_patterns():
    '''one-time method to create ready-to-use patterns with corresponding node_match and edge_match functions'''

    Factory = PatternFactory()

    prepared_patterns = []
    for pattern_id, pattern in Factory.patterns.items():
        pattern_graph, node_match, edge_match = pattern()
        prepared_patterns.append((pattern_id, (pattern_graph, node_match, edge_match)))

    return prepared_patterns

@timer
def extract_claims(serif_doc, prepared_patterns, visualize=False):
    '''
    :param serif_doc:
    :param visualize: whether to generate a pyviz visualization of graph
    :return: list[subgraph_pattern_matching.match_wrapper.MatchWrapper]
    '''

    GB = GraphBuilder()
    document_graph = GB.serif_doc_to_networkx(serif_doc)
    if visualize:
        GB.visualize_networkx_graph(document_graph)

    matches = []
    for (pattern_id, (pattern_graph, node_match, edge_match)) in prepared_patterns:

        pattern_matcher = nx.algorithms.isomorphism.DiGraphMatcher(document_graph, pattern_graph,
                                                                   node_match=node_match,
                                                                   edge_match=edge_match)
        pattern_match_dicts = [g for g in pattern_matcher.subgraph_isomorphisms_iter()]

        # TODO create on-match-filter API that is not ad-hoc
        ###########################################################################################################
        if pattern_id == 'relaxed_ccomp':
            from match_utils.on_match_filters import is_ancestor
            pattern_match_dicts = [m for m in pattern_match_dicts if is_ancestor(match_node_id_to_pattern_node_id=m,
                                                                                 document_graph=document_graph,
                                                                                 ancestor_id=PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                                                                                 descendant_id=PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID)]
        ###########################################################################################################

        pattern_match_dicts = list(map(dict, set(tuple(sorted(m.items())) for m in pattern_match_dicts)))  # deduplicate (sanity check)
        pattern_matches = [MatchWrapper(m, pattern_id, serif_doc) for m in pattern_match_dicts]
        logging.debug("%s - %d", pattern_id, len(pattern_matches))

        matches.extend(pattern_matches)

    return matches


@timer
def main(args):

    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    all_matches = []
    prepared_patterns = prepare_patterns()
    for serifxml_path in serifxml_paths:
        logging.info(serifxml_path)
        serif_doc = serifxml3.Document(serifxml_path)
        all_matches.extend(extract_claims(serif_doc, prepared_patterns, visualize=args.visualize))

    match_corpus = MatchCorpus(all_matches)
    match_corpus.extraction_stats()
    # match_corpus.count_intersentence_conceiver_event_edges()

    # conceiver_event_mtras = match_corpus.to_mtra_pairs()
    # print(conceiver_event_mtras)

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
    PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python \
    python3 \
    /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/extract_claims.py \
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