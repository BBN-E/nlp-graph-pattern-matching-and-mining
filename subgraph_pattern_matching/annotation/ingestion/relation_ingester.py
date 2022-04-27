from annotation.annotation import MentionAnnotation, EntityEntityRelationAnnotation
from annotation.ingestion.ingester import SentenceIngester


TACRED = {
    'TRAIN': '/nfs/raid90/u10/users/brozonoy-ad/data/tacred/serifxml/train.xml',
    'DEV': '/nfs/raid90/u10/users/brozonoy-ad/data/tacred/serifxml/dev.xml',
    'TEST': '/nfs/raid90/u10/users/brozonoy-ad/data/tacred/serifxml/test.xml'
}


class RelationIngester(SentenceIngester):

    def __init__(self):
        super().__init__()

    def ingest_tacred(self):
        return self.ingest_serifxml(TACRED)

    def split_to_annotations(self, split_serif_doc, split_nx_graphs):

        annotations_for_split = []
        for i, serif_sentence in enumerate(split_serif_doc.sentences):

            nx_graph = split_nx_graphs[i]

            if serif_sentence.mention_set:
                for rel_mention in serif_sentence.rel_mention_set:

                    if rel_mention.left_mention.tokens and rel_mention.right_mention.tokens:

                        left_token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in rel_mention.left_mention.tokens]
                        right_token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in rel_mention.right_mention.tokens]

                        left_mention_annotation = MentionAnnotation(networkx_graph=nx_graph,
                                                                    token_node_ids=left_token_node_ids,
                                                                    serif_doc=split_serif_doc,
                                                                    serif_sentence=serif_sentence,
                                                                    entity_type=rel_mention.left_mention.entity_type)

                        right_mention_annotation = MentionAnnotation(networkx_graph=nx_graph,
                                                                     token_node_ids=right_token_node_ids,
                                                                     serif_doc=split_serif_doc,
                                                                     serif_sentence=serif_sentence,
                                                                     entity_type=rel_mention.left_mention.entity_type)

                        relation_annotation = EntityEntityRelationAnnotation(nx_graph, left_mention_annotation, right_mention_annotation, rel_mention.type)
                        annotations_for_split.append(relation_annotation)
