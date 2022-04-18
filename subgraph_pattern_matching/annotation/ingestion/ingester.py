import serifxml3
from abc import ABC
from graph_builder import GraphBuilder
from abc import abstractmethod

from annotation.annotation import MentionAnnotation
from annotation.annotation_corpus import AnnotationCorpus
from tqdm import tqdm


class Ingester(ABC):

    def __init__(self):
        self.graph_builder = GraphBuilder()


class SentenceIngester(Ingester):

    def __init__(self):
        super().__init__()

    def ingest_serifxml(self, data):
        train_serif_doc = serifxml3.Document(data['TRAIN'])
        train_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(train_serif_doc)

        dev_serif_doc = serifxml3.Document(data['DEV'])
        dev_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(dev_serif_doc)

        test_serif_doc = serifxml3.Document(data['TEST'])
        test_nx_graphs = self.graph_builder.serif_doc_to_networkx_per_sentence(test_serif_doc)

        train_annotations = self.split_to_annotations(train_serif_doc, train_nx_graphs)
        dev_annotations = self.split_to_annotations(dev_serif_doc, dev_nx_graphs)
        test_annotations = self.split_to_annotations(test_serif_doc, test_nx_graphs)

        return AnnotationCorpus(train_annotations, dev_annotations, test_annotations)

    @abstractmethod
    def split_to_annotations(self, split_serif_doc, split_nx_graphs):
        '''

        :param split_serif_doc: serifxml3.serif.theory.Document
        :param split_nx_graphs: list[networkx.classes.digraph.DiGraph]
        :return: annotation.annotation_corpus.AnnotationCorpus
        '''
        pass


class DocumentIngester(Ingester):

    def __init__(self):
        super().__init__()

    def ingest_serifxmls_from_list(self, data):
        train_serif_docs, train_nx_graphs = self.get_nx_graphs_from_serif_list(data['TRAIN'])
        dev_serif_docs, dev_nx_graphs = self.get_nx_graphs_from_serif_list(data['DEV'])
        test_serif_docs, test_nx_graphs = self.get_nx_graphs_from_serif_list(data['TEST'])

        train_annotations = self.docs_to_annotations(train_serif_docs, train_nx_graphs)
        dev_annotations = self.docs_to_annotations(dev_serif_docs, dev_nx_graphs)
        test_annotations = self.docs_to_annotations(test_serif_docs, test_nx_graphs)

        return AnnotationCorpus(train_annotations, dev_annotations, test_annotations)

    def get_nx_graphs_from_serif_list(self, serif_list):
        serif_docs = []
        nx_graphs = []
        with open(serif_list, 'r') as serif_list_file:
            lines = serif_list_file.readlines()
            for line in tqdm(lines, desc='building nx graphs from serif'):
                serif_doc = serifxml3.Document(line.strip())
                nx_graph = self.graph_builder.serif_doc_to_networkx(serif_doc)
                nx_graphs.append(nx_graph)
                serif_docs.append(serif_doc)
        return serif_docs, nx_graphs

    @abstractmethod
    def docs_to_annotations(self, serif_docs, nx_graphs):
        '''

       :param serif_docs: list[serifxml3.serif.theory.Document]
       :param nx_graphs: list[networkx.classes.digraph.DiGraph]
       :return: annotation.annotation_corpus.AnnotationCorpus
       '''
        pass