import argparse
import logging
import pickle
import os
from match_wrapper import MatchWrapper, MatchCorpus
from patterns.pattern import Pattern
import serifxml3

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("penman").setLevel(logging.CRITICAL)  # silence penman's default logging (logging.WARNING)


def evaluate(evaluation_corpus, matches_by_serif_id):
    if evaluation_corpus == 'CONLL_ENGLISH':

        from evaluation.datasets.conll import score_conll
        from evaluation.utils import AnnotationScheme
        score_conll(matches_by_serif_id=matches_by_serif_id,
                    SPLIT='TEST',
                    annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION)

    elif evaluation_corpus == 'ACE_ENGLISH':

        from evaluation.datasets.ace import score_ace
        from evaluation.utils import AnnotationScheme
        score_ace(matches_by_serif_id=matches_by_serif_id,
                  SPLIT='TEST',
                  annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION)


    else:
        raise NotImplementedError("Corpus {} not implemented".format(args.evaluation_corpus))

def main(args):
    # read serifxml path(s)
    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    docid_to_doc = {}

    for serifxml_path in serifxml_paths:
        serif_doc = serifxml3.Document(serifxml_path)
        docid_to_doc[serif_doc.docid] = serif_doc

    match_dicts = []
    for pickle_file in os.listdir(args.matches):
        pickled_file_path = os.path.join(args.matches, pickle_file)
        with open(pickled_file_path, 'rb') as f:
            unpickled_matches = pickle.load(f)
        match_dicts.extend(unpickled_matches)

    all_matches = []
    for match_dict in match_dicts:
        match = MatchWrapper(match_node_id_to_pattern_node_id=match_dict['match_node_id_to_pattern_node_id'],
                             pattern=Pattern().load_from_json(match_dict['pattern']),
                             serif_sentence=docid_to_doc[match_dict['docid']].sentences[match_dict['sent_no']],
                             serif_doc=docid_to_doc[match_dict['docid']],
                             category=match_dict['category'])
        all_matches.append(match)

    match_corpus = MatchCorpus(all_matches)
    matches_by_serif_id = match_corpus.organize_matches_by_serif_doc_and_serif_sentence(per_sentence=args.per_sentence)
    evaluate(args.evaluation_corpus, matches_by_serif_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-s', '--per_sentence', action='store_true', help='whether to create nx graphs per individual sentence '
                                                                    'or for entire document (depends on whether the serifxmls'
                                                                    'have document-level parses such as MDP/TDP or not)')
    parser.add_argument('-m', '--matches', type=str, required=True)
    parser.add_argument('-e', '--evaluation_corpus', choices=['TACRED', 'CONLL_ENGLISH', 'ACE_ENGLISH', 'AIDA_TEST'],
                        help='if decoding over an annotated corpus, evaluate accuracy over that dataset',  required=False, default='CONLL_ENGLISH')

    args = parser.parse_args()

    main(args)
