from enum import Enum
from abc import ABC, abstractmethod


##############################################################
#####           ANNOTATION TYPES
##############################################################

class SimpleAnnotationTypes(Enum):

    MENTION = 'MENTION'
    EVENT_TRIGGER = 'EVENT_MENTION'
    EVENT_ARGUMENT = 'EVENT_ARGUMENT'


class FrameAnnotationTypes(Enum):

    EVENT_FRAME = 'EVENT_FRAME'
    ENTITY_ENTITY_RELATION = 'ENTITY_ENTITY_RELATION'
    EVENT_EVENT_RELATION = 'EVENT_EVENT_RELATION'
    CLAIM_FRAME = 'CLAIM_FRAME'


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


class FrameAnnotation(Annotation):

    def __init__(self, networkx_graph, annotation_type):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param annotation_type: annotation.FrameAnnotationTypes.X
        '''

        super().__init__(networkx_graph, annotation_type)

    @property
    def frame(self):
        return self._frame

    @property
    def components(self):
        return self._components

    @property
    def token_node_ids(self):
        return self.all_tokens_as_flat_list

    @property
    def all_tokens_as_nested_list(self):
        return [c.token_node_ids for c in self.components]

    @property
    def all_tokens_as_flat_list(self):
        return [t for c in self.components for t in c.token_node_ids]


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


class EntityEntityRelationAnnotation(FrameAnnotation):

    def __init__(self, networkx_graph, left_entity, right_entity, relation_type):
        super().__init__(networkx_graph, FrameAnnotationTypes.ENTITY_ENTITY_RELATION)
        self._frame = self.EntityEntityRelationFrame(left_entity, right_entity)
        self._components = [left_entity, right_entity]
        self._relation_type = relation_type

    class EntityEntityRelationFrame():
        def __init__(self, left_entity, right_entity):
            self.left_entity = left_entity
            self.right_entity = right_entity

    @property
    def relation_type(self):
        return self._relation_type


# class EventEventRelationAnnotation(FrameAnnotation):
#
#     def __init__(self, networkx_graph, left_event, right_event, relation_type):
#         super().__init__(networkx_graph, FrameAnnotationTypes.EVENT_EVENT_RELATION)
#         self._frame = self.EventEventRelationFrame(left_event, right_event)
#         self._components = [left_event, right_event]
#         self._relation_type = relation_type
#
#     class EventEventRelationFrame():
#         def __init__(self, left_event, right_event):
#             self.left_event = left_event
#             self.right_event = right_event
#
#     @property
#     def relation_type(self):
#         return self._relation_type
#
#     @property
#     def frame(self):
#         return self._frame
#
#     @property
#     def components(self):
#         return self._components


class EventFrameAnnotation(FrameAnnotation):
    def __init__(self, networkx_graph, event_annotation, arg_annotations):
        super().__init__(networkx_graph, FrameAnnotationTypes.EVENT_FRAME)
        self._frame = self.EventFrame(event_annotation, arg_annotations)
        self._components = [event_annotation]
        self._components.extend([a for a in arg_annotations])

    class EventFrame():
        def __init__(self, event, event_arguments):
            self.event = event
            self.event_arguments = event_arguments


# class ClaimFrameAnnotation(FrameAnnotation):
#
#     _annotation_type = FrameAnnotationTypes.CLAIM_FRAME
