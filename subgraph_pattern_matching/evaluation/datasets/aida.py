from sklearn.metrics import classification_report
from itertools import chain

from evaluation.utils import AnnotationScheme, KnowledgeElement, serif_sentence_to_ner_bio_list, \
    serif_sentence_to_bio_list_based_on_predictions
from annotation.ingestion.claim_injester import AIDA_CLAIMS
from annotation.ingestion.claim_injester import ClaimIngester
import networkx as nx

def get_governed_text(match, node_id):
    governed_nodes = nx.dfs_preorder_nodes(match.nx_graph, node_id)

    governed_token_ids = [x.split("__")[1] for x in governed_nodes]
    governed_texts = []  # fill in sentence order
    inGap = True
    for token in match.serif_sentence.token_sequence:
        if token.id in governed_token_ids:
            governed_texts.append(token.text)
            inGap = False
        else:
            if not inGap:
                governed_texts.append("...")
            inGap = True
    # Avoid final "..."
    if governed_texts[-1] == "...":
        governed_texts.pop()
    return " ".join(governed_texts)


def score_aida(matches_by_serif_id, SPLIT='TEST'):
    '''

    :param matches_by_serif_id: {docid: {sent_id: match}}
    :param SPLIT: 'TRAIN', 'DEV', 'TEST'
    :return:
    '''
    aida_corpus = ClaimIngester().ingest_aida(small=True)

    serif_docs = {}

    if SPLIT == 'TRAIN':
        aida_corpus_split = aida_corpus.train_annotations
    elif SPLIT == "DEV":
        aida_corpus_split = aida_corpus.dev_annotations
    elif SPLIT == "TEST":
        aida_corpus_split = aida_corpus.test_annotations
    else:
        raise NotImplementedError

    for annotation in aida_corpus_split:
        cur_serif_id = annotation.serif_doc.docid
        if cur_serif_id not in serif_docs:
            serif_docs[cur_serif_id] = {}
        if annotation.serif_sentence.id not in serif_docs[cur_serif_id]:
            serif_docs[cur_serif_id][annotation.serif_sentence.id] = []
        serif_docs[cur_serif_id][annotation.serif_sentence.id].append(annotation)

    new_claims_found = 0
    old_claims_found = 0
    found_claims = []

    for serif_doc_id, serif_sentence_to_annotation_list in serif_docs.items():

        print(serif_doc_id)
        for sentence_id, matches in matches_by_serif_id[serif_doc_id].items():

            for match in matches:
                # finding tokens for match
                claimant_node_ids = list(match.pattern.get_named_entity_node_ids())
                event_trigger_node_ids = list(match.pattern.get_event_trigger_node_ids())
                assert len(claimant_node_ids) == 1
                assert len(event_trigger_node_ids) == 1
                match_claimant_node_id = match.pattern_node_id_to_match_node_id[claimant_node_ids[0]]
                match_event_node_id =  match.pattern_node_id_to_match_node_id[event_trigger_node_ids[0]]
                claimer_serif_token = match.match_to_serif_theory(match_id=match_claimant_node_id, serif_doc=match.serif_doc)
                event_trigger_serif_token = match.match_to_serif_theory(match_id=match_event_node_id, serif_doc=match.serif_doc)

                governed_text = get_governed_text(match, match_event_node_id)
                governed_author = get_governed_text(match, match_claimant_node_id)
                annotations = serif_sentence_to_annotation_list.get(sentence_id, None)

                if annotations is None:
                    annotations = []

                existing_claim = False
                for annotation in annotations:
                    _, anno_claimer_id = annotation._frame.claimer.token_node_ids[0].split("__")
                    _, anno_event_trigger_id = annotation._frame.claim_trigger.token_node_ids[0].split("__")

                    if anno_claimer_id == claimer_serif_token.id and anno_event_trigger_id == event_trigger_serif_token.id:
                        existing_claim = True
                        print("Match found!")
                        break

                if existing_claim:
                    old_claims_found += 1
                    # print("Old claim:")
                    # print("Author: {}\n Event Trigger: {}\n Inner claim: {}\n Sentence: {}".format(governed_author, event_trigger_serif_token.text, governed_text, match.serif_sentence.text))
                else:
                    new_claims_found += 1
                    # print("New claim:")

                found_claims.append((governed_author, event_trigger_serif_token.text, governed_text, match.serif_sentence.text, existing_claim, match.pattern.pattern_id))

    print("New claims found: {}".format(new_claims_found))
    print("Old claims found: {}".format(old_claims_found))

    output_csv = "/nfs/raid83/u13/caml/users/mselvagg_ad/aida-misc/output_csvs/claims.csv"
    import csv
    with open(output_csv, 'w') as f:
        csvwriter = csv.writer(f, delimiter="|")
        for claim in found_claims:
            csvwriter.writerow(claim)


