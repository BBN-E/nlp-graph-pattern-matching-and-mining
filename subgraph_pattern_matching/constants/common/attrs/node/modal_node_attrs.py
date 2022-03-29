from .node_attrs import NodeAttrs

class ModalNodeAttrs(NodeAttrs):

    special_name = 'specialName'
    mention = 'mention'
    event_mention = 'eventMention'
    value_mention = 'valueMention'
    sentence = 'sentence'
    tokens = 'tokens'
    modal_node_type = 'modalNodeType'
    modal_relation = 'modalRelation'  # relation attr but stored here because ModalTemporalRelationMention stores it
