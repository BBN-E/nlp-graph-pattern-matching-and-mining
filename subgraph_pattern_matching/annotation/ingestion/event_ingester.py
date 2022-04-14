import serifxml3

from graph_builder import GraphBuilder

from annotation.annotation import EventFrameAnnotation, EventTriggerAnnotation, EventArgumentAnnotation
from annotation.annotation_corpus import AnnotationCorpus
from annotation.ingestion.ingester import DocumentIngester

ACE_ENGLISH = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_English/serifxmls/train/serifxmls.list',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_English/serifxmls/dev/serifxmls.list',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_English/serifxmls/test/serifxmls.list',
}

ACE_CHINESE = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/train/serifxmls.list',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/dev/serifxmls.list',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/experiments/expts/datasets_to_serifxml/default/ACE/ACE_Chinese/serifxmls/test/serifxmls.list',
}


class EventIngester(DocumentIngester):

    def __init__(self):
        super().__init__()

    def ingest_ace(self, language='english'):

        if language == 'english':
            ace_data = ACE_ENGLISH
        else:  # language == 'chinese':
            ace_data = ACE_CHINESE

        return self.ingest_serifxmls_from_list(ace_data)

    def docs_to_annotations(self, serif_docs, nx_graphs):

        annotations_for_split = []

        for doc, nx_graph in zip(serif_docs, nx_graphs):

            for i, serif_sentence in enumerate(doc.sentences):

                if serif_sentence.event_mention_set:
                    for event_mention in serif_sentence.event_mention_set:

                        event_argument_annotations = []
                        for event_arg in event_mention.arguments:
                            event_arg_token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in event_arg.mention.tokens]

                            event_argument_annotation = EventArgumentAnnotation(networkx_graph=nx_graph,
                                                                                token_node_ids=event_arg_token_node_ids,
                                                                                role=event_arg.role)
                            event_argument_annotations.append(event_argument_annotation)

                        event_trigger_token_node_ids =  [self.graph_builder.token_to_feats(t)['id'] for t in event_mention.tokens]

                        event_trigger_annotation = EventTriggerAnnotation(networkx_graph=nx_graph,
                                                                          token_node_ids=event_trigger_token_node_ids,
                                                                          event_type=event_mention.event_type)

                        event_frame_annotation = EventFrameAnnotation(nx_graph, event_trigger_annotation, event_argument_annotations)
                        annotations_for_split.append(event_frame_annotation)

        return annotations_for_split
