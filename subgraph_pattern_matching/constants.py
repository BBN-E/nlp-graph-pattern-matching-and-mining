# NOTE: don't include underscore "_" in node/edge names
#       because dotmotif complains; i.e. use "nodeType" instead of
#       "node_type", "CCOMPTOKEN" instead of "CCOMP_TOKEN"

#####################################################
######     Constants for Document Graph        ######
#####################################################


class NodeTypes():

    token = 'token'
    modal = 'modal'
    amr = 'amr'


class EdgeTypes():

    syntax = 'syntax'
    modal = 'modal'
    amr = 'amr'
    modal_constituent_token = 'constituentToken'
    amr_aligned_token = 'amrAlignedToken'


#####################################################


class NodeAttrs():

    id = 'id'
    node_type = 'nodeType'


class TokenNodeAttrs(NodeAttrs):

    text = 'text'
    upos = 'upos'
    xpos = 'xpos'
    index_in_doc = 'indexInDoc'
    incoming_dep_rel = 'incomingDepRel'


class ModalNodeAttrs(NodeAttrs):

    special_name = 'specialName'
    mention = 'mention'
    event_mention = 'eventMention'
    value_mention = 'valueMention'
    sentence = 'sentence'
    tokens = 'tokens'
    modal_node_type = 'modalNodeType'
    modal_relation = 'modalRelation'  # relation attr but stored here because ModalTemporalRelationMention stores it


class AMRNodeAttrs(NodeAttrs):

    varname = 'varname'
    content = 'content'

#####################################################


class EdgeAttrs():

    label = 'label'  # PyVis will visualize 'label' value on edge
    edge_type = 'edgeType'


class SyntaxEdgeAttrs(EdgeAttrs):

    dep_rel = 'depRel'


class ModalEdgeAttrs(EdgeAttrs):

    modal_relation = 'modalRelation'


class AMREdgeAttrs(EdgeAttrs):

    amr_relation = 'amrRelation'


class ModalConstituentTokenEdgeAttrs(EdgeAttrs):
    pass


class AMRAlignedTokenEdgeAttrs(EdgeAttrs):
    pass

#####################################################
######     Constants for Pattern Graphs        ######
#####################################################


class PatternNodeIDs():

    pass


class PatternModalNodeIDs(PatternNodeIDs):

    CONCEIVER_NODE_ID = 'CONCEIVERNODE'
    AUTHOR_CONCEIVER_NODE_ID = 'AUTHORCONCEIVERNODE'
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

    AUTHOR_CONCEIVER_NODE = (PatternModalNodeIDs.AUTHOR_CONCEIVER_NODE_ID,
                             {NodeAttrs.node_type: NodeTypes.modal,
                              ModalNodeAttrs.modal_node_type: 'Conceiver',
                              ModalNodeAttrs.special_name: 'AUTHOR_NODE'})


class PatternTokenNodes(PatternNodes):

    SIP_TOKEN_NODE = (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID,
                      {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.upos: 'VERB'})

    CONCEIVER_TOKEN_NODE = (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
                            {NodeAttrs.node_type: NodeTypes.token})

    EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})

    ROOT_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                             {NodeAttrs.node_type: NodeTypes.token,
                              TokenNodeAttrs.upos: 'VERB|ADJ',
                              TokenNodeAttrs.incoming_dep_rel: 'root'})

    ROOT_VERB_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                    {NodeAttrs.node_type: NodeTypes.token,
                                     TokenNodeAttrs.upos: 'VERB',
                                     TokenNodeAttrs.incoming_dep_rel: 'root'})

    ROOT_ADJ_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                 {NodeAttrs.node_type: NodeTypes.token,
                                  TokenNodeAttrs.upos: 'ADJ',
                                  TokenNodeAttrs.incoming_dep_rel: 'root'})

    CCOMP_VERB_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                   {NodeAttrs.node_type: NodeTypes.token,
                                    TokenNodeAttrs.upos: 'VERB',
                                    TokenNodeAttrs.incoming_dep_rel: 'ccomp'})

    CCOMP_TOKEN_NODE = (PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})  # may be same as event token


class PatternAMRNodes(PatternNodes):
    pass


class PatternEdges():

    # links conceiver meta-node to event meta-node
    CONCEIVER_EVENT_EDGE = (PatternModalNodeIDs.CONCEIVER_NODE_ID, PatternModalNodeIDs.EVENT_NODE_ID,
                            {EdgeAttrs.edge_type: EdgeTypes.modal})

    # links author conceiver meta-node to event meta-node
    AUTHOR_CONCEIVER_EVENT_EDGE = (PatternModalNodeIDs.AUTHOR_CONCEIVER_NODE_ID, PatternModalNodeIDs.EVENT_NODE_ID,
                                   {EdgeAttrs.edge_type: EdgeTypes.modal})

    # links conceiver meta-node to conceiver token
    CONCEIVER_TOKEN_EDGE = (PatternModalNodeIDs.CONCEIVER_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
                            {EdgeAttrs.edge_type: EdgeTypes.modal_constituent_token})

    # links event meta-node to event token
    EVENT_TOKEN_EDGE = (PatternModalNodeIDs.EVENT_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                        {EdgeAttrs.edge_type: EdgeTypes.modal_constituent_token})
