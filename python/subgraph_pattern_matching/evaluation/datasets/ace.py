from itertools import chain

from annotation.ingestion.event_ingester import ACE_ENGLISH
from ...evaluation.utils import AnnotationScheme, KnowledgeElement, create_corpus_directory, \
    serif_sentence_to_event_trigger_bio_list, \
    serif_sentence_to_event_argument_bio_list, serif_sentence_to_bio_list_based_on_predictions
from sklearn.metrics import classification_report


def score_ace(matches_by_serif_id, SPLIT='TEST', annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):

    ace_corpus_dir = create_corpus_directory(ACE_ENGLISH)

    gold_event_trigger_bio = []
    gold_event_argument_bio = []
    pred_event_trigger_bio = []
    pred_event_argument_bio = []

    for gold_serif_doc_id, gold_serif_doc in ace_corpus_dir[SPLIT].items():
        # gold event trigger bio lists
        gold_event_trigger_bio_for_doc = [serif_sentence_to_event_trigger_bio_list(serif_sentence=s,
                                                                                   annotation_scheme=annotation_scheme) \
                                          for s in gold_serif_doc.sentences]
        gold_event_trigger_bio.extend(gold_event_trigger_bio_for_doc)

        # gold event argument bio lists
        gold_event_argument_bio_for_doc = [serif_sentence_to_event_argument_bio_list(serif_sentence=s,
                                                                                     annotation_scheme=annotation_scheme)
                                           for s in gold_serif_doc.sentences]

        # pred event trigger bio lists
        pred_matches = matches_by_serif_id[gold_serif_doc.docid]

        pred_event_trigger_bio_for_doc = [serif_sentence_to_bio_list_based_on_predictions(serif_sentence=s,
                                                                                          matches_for_sentence=
                                                                                          pred_matches[s.id],
                                                                                          ke=KnowledgeElement.EVENT_TRIGGER,
                                                                                          annotation_scheme=annotation_scheme) \
                                          for s in gold_serif_doc.sentences]
        pred_event_trigger_bio.extend(pred_event_trigger_bio_for_doc)

        # pred event argument bio lists
        pred_event_argument_bio_for_doc = [serif_sentence_to_bio_list_based_on_predictions(serif_sentence=s,
                                                                                           matches_for_sentence=
                                                                                           pred_matches[s.id],
                                                                                           ke=KnowledgeElement.EVENT_ARGUMENT,
                                                                                           annotation_scheme=annotation_scheme) \
                                           for s in gold_serif_doc.sentences]

        for i, (g, p) in enumerate(list(zip(gold_event_trigger_bio_for_doc, pred_event_trigger_bio_for_doc))):
            if g != p:
                print(i)
                print(g)
                print(p)
                print("-------------------")
                # import pdb; pdb.set_trace()

        gold_event_argument_bio_for_doc_reformatted = []
        pred_event_argument_bio_for_doc_reformatted = []
        for i, (g, p) in enumerate(list(zip(gold_event_argument_bio_for_doc, pred_event_argument_bio_for_doc))):
            if g != p:
                print(i)
                print(g)
                print(p)
                print("-------------------")
                # import pdb; pdb.set_trace()

            # expands out dictionaries present in IO sequences
            # i.e.   GOLD: ['O', 'O', {'End-Position': 'I-Person', 'Transfer-Money': 'I-Recipient'}, 'O']
            #          --> ['O', 'O', 'I-Person', 'I-Recipient', 'O']
            #        PRED: ['O', 'O', {'Transfer-Money': 'I-Recipient'}, 'O']
            #          --> ['O', 'O', 'O', 'I-Recipient', 'O']
            g_reformatted = []
            p_reformatted = []
            for g_i, p_i in zip(g, p):
                if type(g_i) == dict and type(p_i) == dict:
                    for event_type, arg_type in g_i.items():
                        g_reformatted.append(arg_type)
                        if event_type in p_i and arg_type == p_i[event_type]:
                            p_reformatted.append(arg_type)
                        else:
                            p_reformatted.append("O")
                    for event_type, arg_type in p_i.items():
                        if event_type not in g_i:
                            g_reformatted.append("O")
                            p_reformatted.append(arg_type)
                elif type(g_i) == dict:
                    for event_type, arg_type in g_i.items():
                        g_reformatted.append(arg_type)
                        p_reformatted.append(p_i)
                elif type(p_i) == dict:
                    for event_type, arg_type in p_i.items():
                        g_reformatted.append(g_i)
                        p_reformatted.append(arg_type)
                else:
                    g_reformatted.append(g_i)
                    p_reformatted.append(p_i)

            gold_event_argument_bio_for_doc_reformatted.append(g_reformatted)
            pred_event_argument_bio_for_doc_reformatted.append(p_reformatted)

        gold_event_argument_bio.extend(gold_event_argument_bio_for_doc_reformatted)
        pred_event_argument_bio.extend(pred_event_argument_bio_for_doc_reformatted)

    # event trigger
    print(classification_report(y_true=list(chain(*gold_event_trigger_bio)),
                                y_pred=list(chain(*pred_event_trigger_bio))))

    # event argument
    print(classification_report(y_true=list(chain(*gold_event_argument_bio)),
                                y_pred=list(chain(*pred_event_argument_bio))))
