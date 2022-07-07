from annotation.annotation_base import ClaimFrameAnnotation, EventTriggerAnnotation, MentionAnnotation
from annotation.ingestion.ingester import DocumentIngester

from decode import extract_patterns_from_nx_graph, prepare_patterns, serif_doc_to_nx_graphs
from match_wrapper import MatchWrapper, MatchCorpus
from graph_builder import GraphBuilder

AIDA_CLAIMS = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list.train',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list.dev',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list.test',
}

AIDA_CLAIMS_SMALL = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.train',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.dev',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.test'
}

class ClaimIngester(DocumentIngester):

    def __init__(self, parse_types=None):
        super().__init__(parse_types=parse_types)

    def ingest_aida(self, small=False):
        if small:
            return self.ingest_serifxmls_from_list(AIDA_CLAIMS_SMALL)
        return self.ingest_serifxmls_from_list(AIDA_CLAIMS)

    @staticmethod
    def find_head_token(token_ids, sentence):

        token_node_id_to_token_id = {}
        for token_id in token_ids:
            text, id = token_id.split("__")
            token_node_id_to_token_id[id] = token_id

        head_node_candidates = [token for token in sentence.token_sequence if token.id in token_node_id_to_token_id]

        while len(head_node_candidates) > 1:
            new_head_node_candidates = []

            for token in head_node_candidates:
                if token.head in head_node_candidates:
                    continue
                new_head_node_candidates.append(token)

            # break if multiple candidates found
            if new_head_node_candidates == head_node_candidates:
                break
            head_node_candidates = new_head_node_candidates

        return [token_node_id_to_token_id[token.id] for token in head_node_candidates]

    def docs_to_annotations(self, serif_docs, nx_graphs):

        annotations_for_split = []
        mdp_gb = GraphBuilder(dp=True, amr=False, mdp=True, tdp=False)  # DP+MDP (for claim extraction) by default
        prepared_patterns = prepare_patterns(add_author_patterns=False)

        for serif_doc, nx_graph in zip(serif_docs, nx_graphs):
            mdp_nx_graphs = serif_doc_to_nx_graphs(serif_doc=serif_doc, graph_builder=mdp_gb)
            serif_doc_claim_matches = extract_patterns_from_nx_graph(nx_graph=mdp_nx_graphs[0],
                                                                     serif_doc=serif_doc,
                                                                     serif_sentence=None,
                                                                     patterns=prepared_patterns)

            serif_doc_claim_match_corpus = MatchCorpus(serif_doc_claim_matches)
            conceiver_event_mtras = serif_doc_claim_match_corpus.to_mtra_pairs()
            for (conceiver_mtra, event_mtra) in conceiver_event_mtras:

                if conceiver_mtra.mention is None or event_mtra.event_mention is None:
                    continue

                # filter out cross-sentence claims
                if conceiver_mtra.mention.sentence != event_mtra.event_mention.sentence:
                    continue

                conceiver_token_node_ids = [self.graph_builder.token_to_feats(t)['id']
                                            for t in conceiver_mtra.mention.tokens]

                head_token_node_ids = self.find_head_token(conceiver_token_node_ids, conceiver_mtra.mention.sentence)

                claimer_annotation = MentionAnnotation(networkx_graph=nx_graph,
                                                       token_node_ids=head_token_node_ids,
                                                       serif_doc=serif_doc,
                                                       serif_sentence=conceiver_mtra.mention.sentence,
                                                       entity_type="Claimer")

                event_token_node_ids = [self.graph_builder.token_to_feats(t)['id']
                                        for t in event_mtra.event_mention.tokens]

                claim_annotation = EventTriggerAnnotation(networkx_graph=nx_graph,
                                                          token_node_ids=event_token_node_ids,
                                                          serif_doc=serif_doc,
                                                          serif_sentence=event_mtra.event_mention.sentence,
                                                          serif_event_mention=event_mtra.event_mention,
                                                          event_type=event_mtra.event_mention.event_type)

                claim_frame_annotaton = ClaimFrameAnnotation(networkx_graph=nx_graph,
                                                             serif_doc=serif_doc,
                                                             serif_sentence=event_mtra.event_mention.sentence,
                                                             claimer=claimer_annotation,
                                                             claim_trigger=claim_annotation)

                annotations_for_split.append(claim_frame_annotaton)

        return annotations_for_split
