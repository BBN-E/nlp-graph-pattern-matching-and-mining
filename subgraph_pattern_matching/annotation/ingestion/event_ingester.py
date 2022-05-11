from constants.common.attrs.node.node_attrs import NodeAttrs
from annotation.annotation_base import EventFrameAnnotation, EventTriggerAnnotation, EventArgumentAnnotation
from annotation.ingestion.ingester import DocumentIngester


ACE_ENGLISH = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/ACE_parsed/train.list',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/ACE_parsed/dev.list',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/ACE_parsed/test.list',
}

ACE_CHINESE = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/train/serifxmls.list',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/dev/serifxmls.list',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/test/serifxmls.list',
}

AIDA_TEST = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.train',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.dev',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/doc_processing/LDC2021E11.4-8-2022/text_analytics/serifxml/serif_list_small.test',
}


class EventIngester(DocumentIngester):

    def __init__(self, parse_types=None):
        super().__init__(parse_types=parse_types)

    def ingest_ace(self, language='english'):

        if language == 'english':
            ace_data = ACE_ENGLISH
        else:  # language == 'chinese':
            ace_data = ACE_CHINESE

        return self.ingest_serifxmls_from_list(ace_data)

    def ingest_aida(self):
        return self.ingest_serifxmls_from_list(AIDA_TEST)

    def docs_to_annotations(self, serif_docs, nx_graphs):

        annotations_for_split = []

        for serif_doc, nx_graph in zip(serif_docs, nx_graphs):

            for i, serif_sentence in enumerate(serif_doc.sentences):

                if serif_sentence.event_mention_set:
                    for event_mention in serif_sentence.event_mention_set:

                        if event_mention.event_type == "MTDP_EVENT":
                            continue
                            
                        event_argument_annotations = []
                        for event_arg in event_mention.arguments:
                            event_arg_token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in event_arg.mention.tokens]
                            for token_node_id in event_arg_token_node_ids:
                                nx_graph.nodes[token_node_id][NodeAttrs.annotated] = True
                                nx_graph.nodes[token_node_id][NodeAttrs.event_argument] = event_arg.role

                            event_argument_annotation = EventArgumentAnnotation(networkx_graph=nx_graph,
                                                                                token_node_ids=event_arg_token_node_ids,
                                                                                serif_doc=serif_doc,
                                                                                serif_sentence=serif_sentence,
                                                                                role=event_arg.role)
                            event_argument_annotations.append(event_argument_annotation)

                        event_trigger_token_node_ids =  [self.graph_builder.token_to_feats(t)['id'] for t in event_mention.tokens]
                        for token_node_id in event_trigger_token_node_ids:
                            nx_graph.nodes[token_node_id][NodeAttrs.annotated] = True
                            nx_graph.nodes[token_node_id][NodeAttrs.event_trigger] = event_mention.event_type

                        event_trigger_annotation = EventTriggerAnnotation(networkx_graph=nx_graph,
                                                                          token_node_ids=event_trigger_token_node_ids,
                                                                          serif_doc=serif_doc,
                                                                          serif_sentence=serif_sentence,
                                                                          event_type=event_mention.event_type)

                        event_frame_annotation = EventFrameAnnotation(networkx_graph=nx_graph,
                                                                      serif_doc=serif_doc,
                                                                      serif_sentence=serif_sentence,
                                                                      event_annotation=event_trigger_annotation,
                                                                      arg_annotations=event_argument_annotations)
                        annotations_for_split.append(event_frame_annotation)

        return annotations_for_split
