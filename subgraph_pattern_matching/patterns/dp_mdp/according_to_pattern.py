from .basic_claim_pattern import build_basic_claim_pattern

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from constants.common.types.node_types import NodeTypes
from constants.common.types.edge_types import EdgeTypes

from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs

from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs

from patterns.pattern import Pattern


def according_to_pattern():
    pattern_graph = build_basic_claim_pattern()

    pattern_graph.add_nodes_from([
        ('ACCORDING_TOKEN_NODE',
         {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.text: 'according'})
    ])

    pattern_graph.add_edges_from([

        # EventToken -(obl)-> ConceiverToken
        (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'obl'}),

        # ConceiverToken -(case)-> "according"
        (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID, 'ACCORDING_TOKEN_NODE',
         {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'case'})
    ])

    node_attrs = [ModalNodeAttrs.modal_node_type, TokenNodeAttrs.text]
    edge_attrs = [SyntaxEdgeAttrs.dep_rel]

    # return pattern, node_modal_type_and_text_match, edge_syntactic_relation_match
    return Pattern('according_to_pattern', pattern_graph, node_attrs, edge_attrs)
