import os, json
import argparse
import logging
import networkx as nx
from collections import defaultdict

import serifxml3

from graph_builder import GraphBuilder
from match_wrapper import MatchWrapper, MatchCorpus

from dotmotif import Motif, NetworkXExecutor

from timer import timer


logging.basicConfig(level=logging.INFO)


def prepare_motifs(motif_dir='/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/motifs'):
    '''one-time method to create ready-to-use motifs for matching'''

    id_to_motif = dict()
    for motif_fname in os.listdir(motif_dir):
        motif = Motif(open(os.path.join(motif_dir, motif_fname), 'r').read().strip())
        id_to_motif[motif_fname] = motif
    return id_to_motif


@timer
def extract_claims(serif_doc, prepared_motifs, visualize=False):
    '''
    :param serif_doc:
    :param visualize: whether to generate a pyviz visualization of graph
    :return: list[subgraph_pattern_matching.match_wrapper.MatchWrapper]
    '''

    GB = GraphBuilder()
    document_graph = GB.serif_doc_to_networkx(serif_doc)
    if visualize:
        GB.visualize_networkx_graph(document_graph)

    E = NetworkXExecutor(graph=document_graph)

    matches = []
    for motif_id, motif in prepared_motifs.items():

        pattern_match_dicts = E.find(motif)
        pattern_match_dicts = list(map(dict, set(tuple(sorted(m.items())) for m in pattern_match_dicts)))  # deduplicate (sanity check)
        pattern_match_dicts = [{v:k for k, v in d.items()} for d in pattern_match_dicts]  # reverse in order to initialize MatchWrappers

        # TODO create on-match-filter API that is not ad-hoc
        ###########################################################################################################
        if motif_id == 'relaxed_ccomp':
            from match_utils.on_match_filters import is_ancestor
            pattern_match_dicts = [m for m in pattern_match_dicts if is_ancestor(match_node_id_to_pattern_node_id=m, document_graph=document_graph,
                                                                                 ancestor_id='CCOMPTOKEN', descendant_id='EVENTTOKEN')]
        ###########################################################################################################

        # logging.debug(pattern_match_dicts)
        pattern_matches = [MatchWrapper(m, motif_id, serif_doc) for m in pattern_match_dicts]
        logging.debug("%s - %d", motif_id, len(pattern_matches))

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
    prepared_motifs = prepare_motifs()
    for serifxml_path in serifxml_paths:
        logging.info(serifxml_path)
        serif_doc = serifxml3.Document(serifxml_path)
        all_matches.extend(extract_claims(serif_doc, prepared_motifs, visualize=args.visualize))

    match_corpus = MatchCorpus(all_matches)
    match_corpus.extraction_stats()
    # match_corpus.count_intersentence_conceiver_event_edges()

    # conceiver_event_mtras = match_corpus.to_mtra_pairs()
    # print(conceiver_event_mtras)

    # ccomp_family_random_sample = match_corpus.random_sample({'ccomp', 'relaxed_ccomp', 'relaxed_ccomp_one_hop'}, sample_size=10)
    # according_to_random_sample = match_corpus.random_sample({'according_to'}, sample_size=10)
    
    # for m in ccomp_family_random_sample:
    #     print(m)
    # print("\n\n====================\n====================\n\n")
    # for m in according_to_random_sample:
    #    print(m)


if __name__ == '__main__':
    '''
    PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python \
    python3 \
    /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/extract_claims_with_dotmotif.py \
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
