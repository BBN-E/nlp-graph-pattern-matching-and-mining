from evaluation.utils import create_corpus_directory
from annotation.ingestion.event_ingester import ACE_ENGLISH

def score_ace():

    ace_en_corpus_dir = create_corpus_directory(ACE_ENGLISH)

    # get gold test bio list
    assert len(ace_en_corpus_dir['TEST'].values()) == 1
    gold_test_serif_doc = list(ace_en_corpus_dir['TEST'].values())[0]
    gold_test_bio = [serif_sentence_to_ner_bio_list(s) for s in gold_test_serif_doc.sentences]

    # get pred test bio list
    pred_test_matches = matches_by_serif_id[gold_test_serif_doc.docid]
    pred_test_bio = [serif_sentence_to_ner_bio_list_based_on_predictions(serif_sentence=s,
                                                                         matches_for_sentence=pred_test_matches[s.id]) \
                     for s in gold_test_serif_doc.sentences]

    for g, p in list(zip(gold_test_bio, pred_test_bio))[:10]:
        print(g)
        print(p)
        print("-------------------")
