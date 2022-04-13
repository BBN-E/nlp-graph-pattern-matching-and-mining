import serifxml3

from graph_builder import GraphBuilder

from annotation.annotation import MentionAnnotation
from annotation.annotation_corpus import AnnotationCorpus


CONLL_ENGLISH = {
    'TRAIN': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/eng.train.xml',
    'TESTA': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/eng.testa.xml',
    'TESTB': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/eng.testb.xml'
}

CONLL_SPANISH = {
    'TRAIN': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.train.xml',
    'TESTA': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.testa.xml',
    'TESTB': '/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/esp.testb.xml'
}


class IngestNER():

    def __init__(self):
        self.graph_builder = GraphBuilder()

    def ingest_conll(self, language='english'):

        if language == 'english':

            train_serif_doc = serifxml3.Document(CONLL_ENGLISH['TRAIN'])
            train_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(train_serif_doc)

            dev_serif_doc = serifxml3.Document(CONLL_ENGLISH['TESTA'])
            dev_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(dev_serif_doc)

            test_serif_doc = serifxml3.Document(CONLL_ENGLISH['TESTB'])
            test_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(test_serif_doc)

        else: # language == 'spanish':

            train_serif_doc = serifxml3.Document(CONLL_SPANISH['TRAIN'])
            train_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(train_serif_doc)

            dev_serif_doc = serifxml3.Document(CONLL_SPANISH['TESTA'])
            dev_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(dev_serif_doc)

            test_serif_doc = serifxml3.Document(CONLL_SPANISH['TESTB'])
            test_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(test_serif_doc)

        train_annotations = self.split_to_annotations(train_serif_doc, train_nx_graphs)
        dev_annotations = self.split_to_annotations(dev_serif_doc, dev_nx_graphs)
        test_annotations = self.split_to_annotations(test_serif_doc, test_nx_graphs)

        return AnnotationCorpus(train_annotations, dev_annotations, test_annotations)

    def split_to_annotations(self, split_serif_doc, split_nx_graphs):
        '''

        :param split_serif_doc:
        :param split_nx_graphs:
        :return:
        '''

        annotations_for_split = []
        for i, serif_sentence in enumerate(split_serif_doc.sentences):

            nx_graph = split_nx_graphs[i]

            if serif_sentence.mention_set:
                for mention in serif_sentence.mention_set:

                    if mention.tokens:

                        token_node_ids = [self.graph_builder.token_to_feats(t)['id'] for t in mention.tokens]

                        ner_annotation = MentionAnnotation(networkx_graph=nx_graph,
                                                           token_node_ids=token_node_ids,
                                                           entity_type=mention.entity_type)

                        annotations_for_split.append(ner_annotation)

        return annotations_for_split