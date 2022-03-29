from constants.pattern.id.pattern_modal_node_ids import PatternModalNodeIDs
from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.types.edge_types import EdgeTypes

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
