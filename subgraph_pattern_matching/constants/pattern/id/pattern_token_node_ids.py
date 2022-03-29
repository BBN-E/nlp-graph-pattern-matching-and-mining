from .pattern_node_ids import PatternNodeIDs

class PatternTokenNodeIDs(PatternNodeIDs):

    SIP_TOKEN_NODE_ID = 'SIP'
    CONCEIVER_TOKEN_NODE_ID = 'CONCEIVERTOKEN'
    EVENT_TOKEN_NODE_ID = 'EVENTTOKEN'
    CCOMP_TOKEN_NODE_ID = 'CCOMPTOKEN'  # token that has incoming ccomp relation (could be the same as event token)
