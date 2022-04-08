from .node_attrs import NodeAttrs

class TemporalNodeAttrs(NodeAttrs):

    special_name = 'specialName'
    mention = 'mention'
    event_mention = 'eventMention'
    value_mention = 'valueMention'
    sentence = 'sentence'
    tokens = 'tokens'
    temporal_node_type = 'temporalNodeType'
    temporal_relation = 'temporalRelation'  # relation attr but stored here because ModalTemporalRelationMention stores it
