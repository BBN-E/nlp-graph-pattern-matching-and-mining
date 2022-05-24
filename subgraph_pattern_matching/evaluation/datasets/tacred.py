from sklearn.metrics import classification_report
from itertools import chain

from evaluation.utils import AnnotationScheme, KnowledgeElement, create_corpus_directory, serif_sentence_to_relation_bio_list, \
    serif_sentence_to_bio_list_based_on_predictions
from annotation.ingestion.relation_ingester import TACRED


def score_tacred(matches_by_serif_id, SPLIT='TEST', annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):
    '''

    :param matches_by_serif_id: {docid: {sent_id: match}}
    :param SPLIT: 'TRAIN', 'DEV', 'TEST'
    :return:
    '''

    tacred_corpus_dir = create_corpus_directory(TACRED)

    # get gold test bio list
    assert len(tacred_corpus_dir[SPLIT].values()) == 1
    gold_serif_doc = list(tacred_corpus_dir[SPLIT].values())[0]
    gold_bio = [serif_sentence_to_relation_bio_list(serif_sentence=s,
                                               annotation_scheme=annotation_scheme) \
                for s in gold_serif_doc.sentences]

    # get pred test bio list
    pred_matches = matches_by_serif_id[gold_serif_doc.docid]
    pred_bio = [serif_sentence_to_bio_list_based_on_predictions(serif_sentence=s,
                                                                matches_for_sentence=pred_matches[s.id],
                                                                ke=KnowledgeElement.NAMED_ENTITY,
                                                                annotation_scheme=annotation_scheme,
                                                                append_match_category=True) \
                     for s in gold_serif_doc.sentences]

    for i, (g, p) in enumerate(list(zip(gold_bio, pred_bio))):
        if g != p:
            print(i)
            print(g)
            print(p)
            print("-------------------")
            # import pdb; pdb.set_trace()

    print(classification_report(y_true=list(chain(*gold_bio)),
                                y_pred=list(chain(*pred_bio))))
