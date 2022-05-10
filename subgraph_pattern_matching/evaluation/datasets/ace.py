from sklearn.metrics import classification_report
from itertools import chain

from evaluation.utils import AnnotationScheme, create_corpus_directory, serif_sentence_to_event_trigger_bio_list, serif_sentence_to_event_argument_bio_list, \
    serif_sentence_to_event_trigger_bio_list_based_on_predictions, serif_sentence_to_event_argument_bio_list_based_on_predictions

from annotation.ingestion.event_ingester import ACE_ENGLISH


def score_ace(matches_by_serif_id, SPLIT='TEST', annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):

    ace_corpus_dir = create_corpus_directory(ACE_ENGLISH)

    gold_event_trigger_bio = []
    gold_event_argument_bio = []
    pred_event_trigger_bio = []
    pred_event_argument_bio = []

    for gold_serif_doc_id, gold_serif_doc in ace_corpus_dir[SPLIT].items():

        # get gold test bio lists
        gold_event_trigger_bio.extend([serif_sentence_to_event_trigger_bio_list(serif_sentence=s,
                                                                                annotation_scheme=annotation_scheme) for s in gold_serif_doc.sentences])
        gold_event_argument_bio.extend([serif_sentence_to_event_argument_bio_list(serif_sentence=s,
                                                                                  annotation_scheme=annotation_scheme) for s in gold_serif_doc.sentences])

        # get pred test bio lists
        pred_matches = matches_by_serif_id[gold_serif_doc.docid]
        pred_event_trigger_bio.extend([serif_sentence_to_event_trigger_bio_list_based_on_predictions(serif_sentence=s,
                                                                                                     matches_for_sentence=pred_matches[s.id],
                                                                                                     annotation_scheme=annotation_scheme) \
                                       for s in gold_serif_doc.sentences])
        pred_event_argument_bio.extend([serif_sentence_to_event_argument_bio_list_based_on_predictions(serif_sentence=s,
                                                                                                       matches_for_sentence=pred_matches[s.id],
                                                                                                       annotation_scheme=annotation_scheme) \
                                        for s in gold_serif_doc.sentences])


    for i, (g, p) in enumerate(list(zip(gold_event_trigger_bio, pred_event_trigger_bio)))[:5]:
        if g != p:
            print(i)
            print(g)
            print(p)
            print("-------------------")

    for i, (g, p) in enumerate(list(zip(gold_event_argument_bio, pred_event_argument_bio)))[:5]:
        if g != p:
            print(i)
            print(g)
            print(p)
            print("-------------------")

    # event trigger
    print(classification_report(y_true=list(chain(*gold_event_trigger_bio)),
                                y_pred=list(chain(*pred_event_trigger_bio))))

    # event argument
    print(classification_report(y_true=list(chain(*gold_event_argument_bio)),
                                y_pred=list(chain(*pred_event_argument_bio))))
