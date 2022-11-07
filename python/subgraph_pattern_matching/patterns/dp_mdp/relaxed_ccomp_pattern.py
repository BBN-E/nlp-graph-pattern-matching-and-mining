from ...constants.common.attrs.edge.edge_attrs import EdgeAttrs
from ...constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from ...constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from ...constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from ...constants.common.types.edge_types import EdgeTypes
from ...constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs
from ...constants.pattern.node.pattern_token_nodes import PatternTokenNodes
from ...patterns.pattern import Pattern

from .basic_claim_pattern import build_basic_claim_pattern


def relaxed_ccomp_pattern():
    pattern_graph = build_basic_claim_pattern()

    pattern_graph.add_nodes_from([
        PatternTokenNodes.SIP_TOKEN_NODE,
        PatternTokenNodes.CCOMP_TOKEN_NODE
        # may be the same as event token  # TODO results in the EVENT_TOKEN 1-hop below CCOMP_TOKEN not being matched
    ])

    pattern_graph.add_edges_from([

        # SIP -(nsubj)-> ConceiverToken
        (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

        # TODO results in the EVENT_TOKEN 1-hop below CCOMP_TOKEN not being matched
        # SIP -(ccomp)-> ccompToken
        (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'})
    ])

    node_attrs = [ModalNodeAttrs.modal_node_type,
                  TokenNodeAttrs.upos]

    edge_attrs = [SyntaxEdgeAttrs.dep_rel]

    return Pattern('relaxed_ccomp', pattern_graph, node_attrs, edge_attrs)
