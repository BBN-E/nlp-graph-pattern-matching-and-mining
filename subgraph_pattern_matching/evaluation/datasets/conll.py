from sklearn.metrics import classification_report

from evaluation.utils import create_corpus_directory, serif_sentence_to_ner_bio_list, \
    serif_sentence_to_ner_bio_list_based_on_predictions
from annotation.ingestion.ner_ingester import CONLL_ENGLISH


def score_conll(matches_by_serif_id, SPLIT='TEST', annotation_type='identification'):
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
                                               annotation_scheme='identification') \
                for s in gold_serif_doc.sentences]

    # get pred test bio list
    pred_matches = matches_by_serif_id[gold_serif_doc.docid]
    pred_bio = [serif_sentence_to_ner_bio_list_based_on_predictions(serif_sentence=s,
                                                                    matches_for_sentence=pred_matches[s.id]) \
                     for s in gold_serif_doc.sentences]

    for g, p in list(zip(gold_bio, pred_bio))[:10]:
        print(g)
        print(p)
        print("-------------------")

    print(classification_report(y_true=gold_bio, y_pred=pred_bio))