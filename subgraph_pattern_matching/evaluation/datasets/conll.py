from sklearn.metrics import classification_report
from itertools import chain

from evaluation.utils import AnnotationScheme, create_corpus_directory, serif_sentence_to_ner_bio_list, \
    serif_sentence_to_ner_bio_list_based_on_predictions
from annotation.ingestion.ner_ingester import CONLL_ENGLISH


def score_conll(matches_by_serif_id, SPLIT='TEST', annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):
    '''

    :param matches_by_serif_id: {docid: {sent_id: match}}
    :param SPLIT: 'TRAIN', 'DEV', 'TEST'
    :return:
    '''

    conll_en_corpus_dir = create_corpus_directory(CONLL_ENGLISH)

    # get gold test bio list
    assert len(conll_en_corpus_dir[SPLIT].values()) == 1
    gold_serif_doc = list(conll_en_corpus_dir[SPLIT].values())[0]
    gold_bio = [serif_sentence_to_ner_bio_list(serif_sentence=s,
                                               annotation_scheme=annotation_scheme) \
                for s in gold_serif_doc.sentences]

    # get pred test bio list
    pred_matches = matches_by_serif_id[gold_serif_doc.docid]
    pred_bio = [serif_sentence_to_ner_bio_list_based_on_predictions(serif_sentence=s,
                                                                    matches_for_sentence=pred_matches[s.id],
                                                                    annotation_scheme=annotation_scheme) \
                     for s in gold_serif_doc.sentences]

    for i, (g, p) in enumerate(list(zip(gold_bio, pred_bio))):
        if g != p:
            print(i)
            print(g)
            print(p)
            print("-------------------")

    print(classification_report(y_true=list(chain(*gold_bio)),
                                y_pred=list(chain(*pred_bio))))
