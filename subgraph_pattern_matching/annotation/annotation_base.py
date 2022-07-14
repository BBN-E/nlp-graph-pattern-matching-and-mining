from enum import Enum
from abc import ABC, abstractmethod
from constants.common.attrs.node.node_attrs import NodeAttrs

from constants.special_symbols import ID_DELIMITER


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
    def __init__(self, networkx_graph, serif_doc, serif_sentence, annotation_type):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param serif_doc: serif.theory.document.Document
        :param serif_sentence: serif.theory.sentence.Sentence
        :param annotation_type: annotation.{Simple,Frame}AnnotationTypes.X
        '''

        self._networkx_graph = networkx_graph
        self._serif_doc = serif_doc
        self._serif_sentence = serif_sentence
        self._annotation_type = annotation_type

    @property
    def annotation_type(self):
        return self._annotation_type

    @property
    def networkx_graph(self):
        return self._networkx_graph

    @property
    def serif_doc(self):
        return self._serif_doc

    @property
    def serif_sentence(self):
        return self._serif_sentence

    @property
    @abstractmethod
    def category(self):
        '''annotation category, e.g. "PER", "Attack.Bombing", "org-founder"'''
        pass

    @property
    @abstractmethod
    def token_node_ids_to_node_attr_label(self):
        pass


class SimpleAnnotation(Annotation):

    def __init__(self, networkx_graph, token_node_ids, serif_doc, serif_sentence, annotation_type, node_attr, label):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param token_node_ids: list[str] for annotation token node ids in networkx graph
        :param serif_doc: serif.theory.document.Document
        :param serif_sentence: serif.theory.sentence.Sentence
        :param annotation_type: annotation.SimpleAnnotationTypes.X
        '''

        super().__init__(networkx_graph=networkx_graph,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=annotation_type)
        self._token_node_ids = token_node_ids
        self._label = label
        self._node_attr = node_attr

    @property
    def token_node_ids(self):
        return self._token_node_ids

    @property
    def serif_tokens(self):

        if self._serif_doc:

            _serif_token_ids = [_token_node_id.split(ID_DELIMITER)[-1] for _token_node_id in self._token_node_ids]
            _serif_tokens = [self._serif_doc.lookup_id(_serif_token_id) for _serif_token_id in _serif_token_ids]
            return _serif_tokens

        return None

    @property
    def token_node_ids_to_node_attr_label(self):
        token_node_ids_to_node_attr_label = {}
        for t in self._token_node_ids:
            token_node_ids_to_node_attr_label[t] = [(self._node_attr, self._label)]
        return token_node_ids_to_node_attr_label

    @property
    def category(self):
        return self._label


class FrameAnnotation(Annotation):

    def __init__(self, networkx_graph, serif_doc, serif_sentence, annotation_type):
        '''

        :param networkx_graph: networkx.classes.digraph.DiGraph
        :param serif_doc: serif.theory.document.Document
        :param serif_sentence: serif.theory.sentence.Sentence
        :param annotation_type: annotation.FrameAnnotationTypes.X
        '''

        super().__init__(networkx_graph=networkx_graph,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=annotation_type)

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
    def token_node_ids_to_node_attr_label(self):
        token_node_id_to_annotation_type = {}
        for c in self.components:
            for t, attr_label_list in c.token_node_ids_to_node_attr_label.items():
                if t not in token_node_id_to_annotation_type:
                    token_node_id_to_annotation_type[t] = [attr_label_list[0]]
                else:
                    token_node_id_to_annotation_type[t].append(attr_label_list[0])
        return token_node_id_to_annotation_type


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

    def __init__(self, networkx_graph, token_node_ids, serif_doc, serif_sentence, entity_type):
        super().__init__(networkx_graph=networkx_graph,
                         token_node_ids=token_node_ids,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=SimpleAnnotationTypes.MENTION,
                         node_attr=NodeAttrs.named_entity,
                         label=entity_type)

    @property
    def entity_type(self):
        return self._label

class EventTriggerAnnotation(SimpleAnnotation):

    def __init__(self, networkx_graph, token_node_ids, serif_doc, serif_sentence, serif_event_mention, event_type):
        super().__init__(networkx_graph=networkx_graph,
                         token_node_ids=token_node_ids,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=SimpleAnnotationTypes.EVENT_TRIGGER,
                         node_attr=NodeAttrs.event_trigger,
                         label=event_type)
        self._serif_event_mention = serif_event_mention

    @property
    def event_type(self):
        return self._label

    @property
    def serif_event_mention(self):
        return self._serif_event_mention


class EventArgumentAnnotation(SimpleAnnotation):

    def __init__(self, networkx_graph, token_node_ids, serif_doc, serif_sentence, serif_event_argument, role):
        super().__init__(networkx_graph=networkx_graph,
                         token_node_ids=token_node_ids,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=SimpleAnnotationTypes.EVENT_ARGUMENT,
                         node_attr=NodeAttrs.event_argument,
                         label=role)
        self._serif_event_argument = serif_event_argument

    @property
    def role(self):
        return self._label

    @property
    def serif_event_argument(self):
        return self._serif_event_argument

# ##############################################################
# #####           FRAME ANNOTATION CLASSES
# ##############################################################


class EntityEntityRelationAnnotation(FrameAnnotation):

    def __init__(self, networkx_graph, serif_doc, serif_sentence, left_entity, right_entity, relation_type):
        super().__init__(networkx_graph=networkx_graph,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=FrameAnnotationTypes.ENTITY_ENTITY_RELATION)
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

    @property
    def category(self):
        return self._relation_type


class EventFrameAnnotation(FrameAnnotation):
    def __init__(self, networkx_graph, serif_doc, serif_sentence, event_annotation, arg_annotations):
        super().__init__(networkx_graph=networkx_graph,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=FrameAnnotationTypes.EVENT_FRAME)
        self._frame = self.EventFrame(event_annotation, arg_annotations)
        self._components = [event_annotation]
        self._components.extend([a for a in arg_annotations])

    class EventFrame():
        def __init__(self, event, event_arguments):
            self.event = event
            self.event_arguments = event_arguments

    @property
    def category(self):
        return self._frame.event.event_type


class ClaimFrameAnnotation(FrameAnnotation):

    def __init__(self, networkx_graph, serif_doc, serif_sentence, claimer, claim_trigger, claim_info=None):
        super().__init__(networkx_graph=networkx_graph,
                         serif_doc=serif_doc,
                         serif_sentence=serif_sentence,
                         annotation_type=FrameAnnotationTypes.CLAIM_FRAME)
        self._frame = self.ClaimFrame(claimer, claim_trigger)
        self._components = [claimer, claim_trigger]
        self.claim_info = claim_info

    class ClaimFrame():
        def __init__(self, claimer, claim_trigger):
            self.claimer = claimer
            self.claim_trigger = claim_trigger

    @property
    def category(self):
        return None
