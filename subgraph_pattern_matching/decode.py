import json
import argparse
import logging
import networkx as nx

import serifxml3

from graph_builder import GraphBuilder
from match_wrapper import MatchWrapper, MatchCorpus
from local_pattern_finder import read_corpus
from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs

from patterns.pattern import Pattern

from utils.timer import timer


logging.basicConfig(level=logging.DEBUG)
logging.getLogger("penman").setLevel(logging.CRITICAL)  # silence penman's default logging (logging.WARNING)


def prepare_patterns():

    from patterns.dp_mdp.ccomp_pattern import ccomp_pattern
    from patterns.dp_mdp.relaxed_ccomp_pattern import relaxed_ccomp_pattern
    from patterns.dp_mdp.relaxed_ccomp_one_hop_pattern import relaxed_ccomp_one_hop_pattern
    from patterns.dp_mdp.according_to_pattern import according_to_pattern
    from patterns.dp_mdp.author_conceiver_event_edge_0_pattern import author_conceiver_event_edge_pattern_0
    from patterns.dp_mdp.author_conceiver_event_edge_1_pattern import author_conceiver_event_edge_pattern_1
    from patterns.dp_mdp.author_conceiver_event_edge_2_pattern import author_conceiver_event_edge_pattern_2
    from patterns.dp_mdp.author_conceiver_event_edge_3_pattern import author_conceiver_event_edge_pattern_3
    from patterns.dp_mdp.as_reported_by_pattern import as_reported_by_pattern
    from patterns.dp_mdp.grounded_conceiver_event_edge_pattern import grounded_conceiver_event_edge_pattern
    from patterns.amr.person_says_x_pattern import person_says_x_pattern

    patterns = [ccomp_pattern(),
                relaxed_ccomp_pattern(),
                relaxed_ccomp_one_hop_pattern(),
                according_to_pattern(),
                # author_conceiver_event_edge_pattern_0,
                author_conceiver_event_edge_pattern_1(),
                author_conceiver_event_edge_pattern_2(),
                author_conceiver_event_edge_pattern_3(),
                as_reported_by_pattern()]

    basic_patterns = [grounded_conceiver_event_edge_pattern()]

    # amr_patterns = self.create_propbank_frames_patterns()
    amr_patterns = [person_says_x_pattern()]

    return patterns


def prepare_serialized_patterns(patterns_json_path='/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/4-26-22-conll-edge/all_patterns.json'):

    with open(patterns_json_path, 'r') as f:
        json_patterns = json.load(f)

    patterns = []
    for json_dict in json_patterns:
        p = Pattern()
        p.load_from_json(json_dict)
        patterns.append(p)

    return patterns


def serif_doc_to_nx_graphs(serif_doc, graph_builder, per_sentence=False):
    '''
    :param serif_doc:
    :param graph_builder: graph_builder.GraphBuilder
    :param per_sentence: boolean indicating whether nx graphs should be created per sentence (depends on dataset)
    :return:
    '''

    if per_sentence:
        nx_graphs = graph_builder.serif_doc_to_networkx_per_sentence(serif_doc=serif_doc)
    else:
        nx_graphs = [graph_builder.serif_doc_to_networkx(serif_doc=serif_doc)]

    return nx_graphs


def extract_patterns_from_nx_graph(nx_graph, patterns, serif_doc, serif_sentence):
    '''

    :param nx_graph:
    :param patterns:
    :param serif_doc:
    :param serif_sentence:
    :return: list[subgraph_pattern_matching.match_wrapper.MatchWrapper]
    '''

    matches = []
    for pattern in patterns:

        pattern_id = pattern.pattern_id
        logging.info(pattern_id)

        pattern_matcher = nx.algorithms.isomorphism.DiGraphMatcher(nx_graph, pattern.pattern_graph,
                                                                   node_match=pattern.node_match,
                                                                   edge_match=pattern.edge_match)
        pattern_match_dicts = [g for g in pattern_matcher.subgraph_isomorphisms_iter()]

        # TODO create on-match-filter API that is not ad-hoc
        ###########################################################################################################
        if pattern_id == 'relaxed_ccomp':
            from match_utils.on_match_filters import is_ancestor
            pattern_match_dicts = [m for m in pattern_match_dicts if is_ancestor(match_node_id_to_pattern_node_id=m,
                                                                                 document_graph=nx_graph,
                                                                                 ancestor_id=PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                                                                                 descendant_id=PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID)]
        ###########################################################################################################

        pattern_match_dicts = list(map(dict, set(tuple(sorted(m.items())) for m in pattern_match_dicts)))  # deduplicate (sanity check)
        pattern_matches = [MatchWrapper(match_node_id_to_pattern_node_id=m,
                                        pattern_id=pattern_id,
                                        serif_sentence=serif_sentence,
                                        serif_doc=serif_doc) for m in pattern_match_dicts]
        if len(pattern_matches) > 0:
            logging.info("%s - %d", pattern_id, len(pattern_matches))

        matches.extend(pattern_matches)

    return matches


def main(args):

    # read serifxml path(s)
    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    # GraphBuilder object to construct nx graphs from parsed serif docs
    GB = GraphBuilder()

    # create patterns
    if args.patterns_path:
        patterns = prepare_serialized_patterns(patterns_json_path=args.patterns_path)
    else:
        patterns = prepare_patterns()

    # extract patterns from every serifxml
    all_matches = []
    for serifxml_path in serifxml_paths:

        logging.info(serifxml_path)

        # create serif_doc and convert to networkx graph(s)
        serif_doc = serifxml3.Document(serifxml_path)
        nx_graphs = serif_doc_to_nx_graphs(serif_doc=serif_doc,
                                           graph_builder=GB,
                                           per_sentence=args.per_sentence)

        # do subgraph pattern matching for every nx graph
        if args.per_sentence:
            for nx_graph, serif_sentence in list(zip(nx_graphs, serif_doc.sentences))[:10]:
                logging.info("doc:{}/sentence:{}".format(serif_doc.docid, serif_sentence.id))
                all_matches.extend(extract_patterns_from_nx_graph(nx_graph=nx_graph,
                                                                  serif_doc=serif_doc,
                                                                  serif_sentence=serif_sentence,
                                                                  patterns=patterns))
        else:  # per-document
            logging.info("doc:{}".format(serif_doc.docid))
            all_matches.extend(extract_patterns_from_nx_graph(nx_graph=nx_graphs[0],
                                                              serif_doc=serif_doc,
                                                              serif_sentence=None,
                                                              patterns=patterns))

    match_corpus = MatchCorpus(all_matches)
    matches_by_serif_id = match_corpus.organize_matches_by_serif_doc_and_serif_sentence(per_sentence=args.per_sentence)

    # if decoding over annotated corpus, ingest gold corpus and do evaluation
    if args.evaluation_corpus:

        from evaluation.utils import create_corpus_directory, serif_sentence_to_ner_bio_list, \
            serif_sentence_to_ner_bio_list_based_on_predictions

        if args.evaluation_corpus == 'CONLL_ENGLISH':

            from annotation.ingestion.ner_ingester import CONLL_ENGLISH
            conll_en_corpus_dir = create_corpus_directory(CONLL_ENGLISH)

            # # get gold dev bio list
            # assert len(conll_en_corpus_dir['DEV'].values()) == 1
            # gold_dev_serif_doc = list(conll_en_corpus_dir['DEV'].values())[0]
            # gold_dev_bio = [serif_sentence_to_ner_bio_list(serif_sentence=s) for s in gold_dev_serif_doc.sentences]
            #
            # # get pred dev bio list
            # pred_dev_matches = matches_by_serif_id[gold_dev_serif_doc.id]
            # pred_dev_bio = [serif_sentence_to_ner_bio_list_based_on_predictions(serif_sentence=s,
            #                                                                    matches_for_sentence=pred_dev_matches[s.id]) \
            #                for s in gold_dev_serif_doc.sentences]

            # get gold test bio list
            assert len(conll_en_corpus_dir['TEST'].values()) == 1
            gold_test_serif_doc = list(conll_en_corpus_dir['TEST'].values())[0]
            gold_test_bio = [serif_sentence_to_ner_bio_list(s) for s in gold_test_serif_doc.sentences]

            # get pred test bio list
            pred_test_matches = matches_by_serif_id[gold_test_serif_doc.id]
            pred_test_bio = [serif_sentence_to_ner_bio_list_based_on_predictions(serif_sentence=s,
                                                                                 matches_for_sentence=pred_test_matches[s.id]) \
                            for s in gold_test_serif_doc.sentences]

            for g,p in list(zip(gold_test_bio, pred_test_bio))[:10]:
                print(g)
                print(p)
                print("-------------------")

        else:
            raise NotImplementedError("Corpus {} not implemented".format(args.evaluation_corpus))


if __name__ == '__main__':
    '''
    PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python \
    python3 \
    /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/decode.py \
    -i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/lists/modal.serifxml.with_amr.all \
    -l
    '''

    '''
    PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python \
    python3 \
    /nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/decode.py \
    -i /nfs/raid83/u13/caml/users/mselvagg_ad/data/conll/eng/eng.testb.xml \
    -s \
    -p /nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/4-26-22-conll-edge/all_patterns.json \
    -e CONLL_ENGLISH
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-s', '--per_sentence', action='store_true', help='whether to create nx graphs per individual sentence '
                                                                    'or for entire document (depends on whether the serifxmls'
                                                                    'have document-level parses such as MDP/TDP or not)')
    parser.add_argument('-p', '--patterns_path', help='path to serialized patterns to use for extraction',
                        default='/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/4-26-22-conll-edge/all_patterns.json')
    parser.add_argument('-e', '--evaluation_corpus', choices=['TACRED', 'CONLL_ENGLISH', 'ACE_ENGLISH', 'AIDA_TEST'],
                        help='if decoding over an annotated corpus, evaluate accuracy over that dataset',  required=False, default='CONLL_ENGLISH')
    # parser.add_argument('-o', '--output', type=str)
    args = parser.parse_args()

    main(args)
