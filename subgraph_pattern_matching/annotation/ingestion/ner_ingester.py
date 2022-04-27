from annotation.annotation import MentionAnnotation
from annotation.ingestion.ingester import SentenceIngester

CONLL_ENGLISH = {
    'TRAIN': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/conll/eng/eng.train.xml',
    'DEV': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/conll/eng/eng.testa.xml',
    'TEST': '/nfs/raid83/u13/caml/users/mselvagg_ad/data/conll/eng/eng.testb.xml'
}

CONLL_SPANISH = {
    'TRAIN': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.train.xml',
    'DEV': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.testa.xml',
    'TEST': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.testb.xml'
}


class NERIngester(SentenceIngester):

    def __init__(self):
        super().__init__()

    def ingest_conll(self, language='english'):

        if language == 'english':
            conll_data = CONLL_ENGLISH
        else:  # language == 'spanish':
            conll_data = CONLL_SPANISH

        return self.ingest_serifxml(conll_data)

    def split_to_annotations(self, split_serif_doc, split_nx_graphs):

        annotations_for_split = []
        for i, serif_sentence in enumerate(split_serif_doc.sentences):

            nx_graph = split_nx_graphs[i]

            if serif_sentence.mention_set:
                for mention in serif_sentence.mention_set:

                    if mention.tokens:

                        token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in mention.tokens]

                        ner_annotation = MentionAnnotation(networkx_graph=nx_graph,
                                                           token_node_ids=token_node_ids,
                                                           serif_doc=split_serif_doc,
                                                           serif_sentence=serif_sentence,
                                                           entity_type=mention.entity_type)

                        annotations_for_split.append(ner_annotation)

        return annotations_for_split