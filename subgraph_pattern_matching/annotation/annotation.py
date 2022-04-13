from enum import Enum
from abc import ABC, abstractmethod


##############################################################
#####           ANNOTATION TYPES
##############################################################

class SimpleAnnotationTypes(Enum):

    MENTION = 'MENTION'
    EVENT_TRIGGER = 'EVENT_MENTION'
    EVENT_ARGUMENT = 'EVENT_ARGUMENT'


# class FrameAnnotationTypes(Enum):
#
#     EVENT_FRAME = 'EVENT_FRAME'
#     ENTITY_ENTITY_RELATION = 'ENTITY_ENTITY_RELATION'
#     EVENT_EVENT_RELATION = 'EVENT_EVENT_RELATION'
#     CLAIM_FRAME = 'CLAIM_FRAME'


##############################################################
#####           ABSTRACT ANNOTATION CLASSES
##############################################################

class Annotation(ABC):

    @abstractmethod
    def __init__(self, networkx_graph, annotation_type):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param annotation_type: annotation.{Simple,Frame}AnnotationTypes.X
        '''

        self._networkx_graph = networkx_graph
        self._annotation_type = annotation_type

    @property
    def annotation_type(self):
        return self._annotation_type

    @property
    def networkx_graph(self):
        return self._networkx_graph


class SimpleAnnotation(Annotation):

    def __init__(self, networkx_graph, token_node_ids, annotation_type):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param token_node_ids: list[str] for annotation token node ids in networkx graph
        :param annotation_type: annotation.SimpleAnnotationTypes.X
        '''

        super().__init__(networkx_graph, annotation_type)
        self._token_node_ids = token_node_ids

    @property
    def token_node_ids(self):
        return self._token_node_ids


# class FrameAnnotation(Annotation):
#
#     @property
#     @abstractmethod
#     def frame(self):
#         pass
#
#     @property
#     @abstractmethod
#     def components(self):
#         pass
#
#     @property
#     def all_tokens_as_flat_list(self):
#         return [c.tokens for c in self.components]
#
#     @property
#     def all_tokens_as_nested_list(self):
#         return [t for c in self.components for t in c.tokens]


##############################################################
#####           SIMPLE ANNOTATION CLASSES
##############################################################

class MentionAnnotation(SimpleAnnotation):

    def __init__(self, networkx_graph, token_node_ids, entity_type):
        super().__init__(networkx_graph, token_node_ids, SimpleAnnotationTypes.MENTION)
        self._entity_type = entity_type

    @property
    def entity_type(self):
        return self._entity_type


class EventTriggerAnnotation(SimpleAnnotation):

    def __init__(self, networkx_graph, token_node_ids, event_type):
        super().__init__(networkx_graph, token_node_ids, SimpleAnnotationTypes.EVENT_TRIGGER)
        self._event_type = event_type

    @property
    def event_type(self):
        return self._event_type


class EventArgumentAnnotation(SimpleAnnotation):

    def __init__(self, networkx_graph, token_node_ids, role):
        super().__init__(networkx_graph, token_node_ids, SimpleAnnotationTypes.EVENT_ARGUMENT)
        self._role = role

    @property
    def role(self):
        return self._role


# ##############################################################
# #####           FRAME ANNOTATION CLASSES
# ##############################################################
#
# class EntityEntityRelationAnnotation(FrameAnnotation):
#
#     _annotation_type = FrameAnnotationTypes.ENTITY_ENTITY_RELATION
#
#
# class EventEventRelationAnnotation(FrameAnnotation):
#
#     _annotation_type = FrameAnnotationTypes.EVENT_EVENT_RELATION
#
#
# class EventFrameAnnotation(FrameAnnotation):
#
#     _annotation_type = FrameAnnotationTypes.EVENT_FRAME
#
#
# class ClaimFrameAnnotation(FrameAnnotation):
#
#     _annotation_type = FrameAnnotationTypes.CLAIM_FRAME

if __name__ == '__main__':
    import networkx as nx
    G = nx.DiGraph()
    ma = MentionAnnotation(G, ['a', 'b', 'c'], 'PER')
    import pdb; pdb.set_trace()