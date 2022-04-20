from .basic_claim_pattern import build_basic_claim_pattern

from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from constants.common.types.edge_types import EdgeTypes

from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes

from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from patterns.pattern import Pattern

def relaxed_ccomp_one_hop_pattern():
    pattern_graph = build_basic_claim_pattern()

    pattern_graph.add_nodes_from([
        PatternTokenNodes.SIP_TOKEN_NODE,
        PatternTokenNodes.CCOMP_TOKEN_NODE  # parent of event token
    ])

    pattern_graph.add_edges_from([

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

    node_attrs = [ModalNodeAttrs.modal_node_type,
                  TokenNodeAttrs.upos]

    edge_attrs = [SyntaxEdgeAttrs.dep_rel]

    return Pattern('relaxed_ccomp_one_hop', pattern_graph, node_attrs, edge_attrs)
