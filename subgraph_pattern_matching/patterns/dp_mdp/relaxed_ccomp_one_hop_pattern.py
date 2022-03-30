from .basic_claim_pattern import build_basic_claim_pattern

from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from constants.common.types.edge_types import EdgeTypes

from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes

from match_utils.node_match_functions import node_multiple_attrs_match, node_modal_type_match, node_upos_match
from match_utils.edge_match_functions import edge_syntactic_relation_match


def relaxed_ccomp_one_hop_pattern():
    pattern = build_basic_claim_pattern()

    pattern.add_nodes_from([
        PatternTokenNodes.SIP_TOKEN_NODE,
        PatternTokenNodes.CCOMP_TOKEN_NODE  # parent of event token
    ])

    pattern.add_edges_from([

        # SIP -(nsubj)-> ConceiverToken
        (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

        # SIP -(ccomp)-> ccompToken
        (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'}),

        # ccompToken -()-> EventToken
        (PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax})
    ])

    return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                              node_upos_match), edge_syntactic_relation_match
