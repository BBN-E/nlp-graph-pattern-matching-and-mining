

class NodeTypes():

    token = 'token'
    modal = 'modal'


class EdgeTypes():

    syntax = 'syntax'
    modal = 'modal'
    constituent_token = 'constituent_token'


####################################################


class BasicNodeAttrs():

    id = 'id'
    node_type = 'node_type'


class TokenNodeAttrs():

    text = 'text'
    upos = 'upos'
    xpos = 'xpos'
    index_in_doc = 'index_in_doc'


class ModalNodeAttrs():

    special_name = 'special_name'
    mention = 'mention'
    event_mention = 'event_mention'
    value_mention = 'value_mention'
    sentence = 'sentence'
    tokens = 'tokens'
    modal_node_type = 'modal_node_type'
    modal_relation = 'modal_relation'  # relation attr but stored here because ModalTemporalRelationMention stores it


####################################################


class BasicEdgeAttrs():

    label = 'label'  # PyVis will visualize 'label' value on edge
    edge_type = 'edge_type'


class SyntaxEdgeAttrs():

    dep_rel = 'dep_rel'


class ModalEdgeAttrs():

    modal_relation = 'modal_relation'