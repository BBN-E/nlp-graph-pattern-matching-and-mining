#####################################################
######     Constants for Document Graph        ######
#####################################################


class NodeTypes():

    token = 'token'
    modal = 'modal'


class EdgeTypes():

    syntax = 'syntax'
    modal = 'modal'
    constituent_token = 'constituentToken'


#####################################################


class NodeAttrs():

    id = 'id'
    node_type = 'nodeType'


class TokenNodeAttrs(NodeAttrs):

    text = 'text'
    upos = 'upos'
    xpos = 'xpos'
    index_in_doc = 'indexInDoc'


class ModalNodeAttrs(NodeAttrs):

    special_name = 'specialName'
    mention = 'mention'
    event_mention = 'eventMention'
    value_mention = 'valueMention'
    sentence = 'sentence'
    tokens = 'tokens'
    modal_node_type = 'modalNodeType'
    modal_relation = 'modalRelation'  # relation attr but stored here because ModalTemporalRelationMention stores it


#####################################################


class EdgeAttrs():

    label = 'label'  # PyVis will visualize 'label' value on edge
    edge_type = 'edgeType'


class SyntaxEdgeAttrs(EdgeAttrs):

    dep_rel = 'depRel'


class ModalEdgeAttrs(EdgeAttrs):

    modal_relation = 'modalRelation'


class ConstituentTokenEdgeAttrs(EdgeAttrs):

    pass


#####################################################
######     Constants for Pattern Graphs        ######
#####################################################


class PatternNodeIDs():

    pass


class PatternModalNodeIDs(PatternNodeIDs):

    CONCEIVER_NODE_ID = 'CONCEIVERNODE'
    EVENT_NODE_ID = 'EVENTNODE'
    EVENT_SIP_NODE_ID = 'EVENTSIPNODE'


class PatternTokenNodeIDs(PatternNodeIDs):

    SIP_TOKEN_NODE_ID = 'SIP'
    CONCEIVER_TOKEN_NODE_ID = 'CONCEIVERTOKEN'
    EVENT_TOKEN_NODE_ID = 'EVENTTOKEN'
    CCOMP_TOKEN_NODE_ID = 'CCOMPTOKEN'  # token that has incoming ccomp relation (could be the same as event token)


#####################################################


class PatternNodes():

    pass


class PatternModalNodes(PatternNodes):

    CONCEIVER_NODE = (PatternModalNodeIDs.CONCEIVER_NODE_ID,
                      {NodeAttrs.node_type: NodeTypes.modal, ModalNodeAttrs.modal_node_type: 'Conceiver'})

    EVENT_NODE = (PatternModalNodeIDs.EVENT_NODE_ID,
                  {NodeAttrs.node_type: NodeTypes.modal, ModalNodeAttrs.modal_node_type: 'Event'})


class PatternTokenNodes(PatternNodes):

    SIP_TOKEN_NODE = (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID,
                      {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.upos: 'VERB'})

    CONCEIVER_TOKEN_NODE = (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
                            {NodeAttrs.node_type: NodeTypes.token})

    EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})

    CCOMP_TOKEN_NODE = (PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})  # may be same as event token


class PatternEdges():

    # links conceiver meta-node to event meta-node
    CONCEIVER_EVENT_EDGE = (PatternModalNodeIDs.CONCEIVER_NODE_ID, PatternModalNodeIDs.EVENT_NODE_ID,
                            {EdgeAttrs.edge_type: EdgeTypes.modal})

    # links conceiver meta-node to conceiver token
    CONCEIVER_TOKEN_EDGE = (PatternModalNodeIDs.CONCEIVER_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
                            {EdgeAttrs.edge_type: EdgeTypes.constituent_token})

    # links event meta-node to event token
    EVENT_TOKEN_EDGE = (PatternModalNodeIDs.EVENT_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                        {EdgeAttrs.edge_type: EdgeTypes.constituent_token})
