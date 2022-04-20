import networkx as nx

from constants.pattern.node.pattern_modal_nodes import PatternModalNodes
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes
from constants.pattern.edge.pattern_edges import PatternEdges

from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from patterns.pattern import Pattern

def author_conceiver_event_edge_pattern_2():
    '''event token is ADJ with incoming root relation'''

    pattern_graph = nx.DiGraph()

    pattern_graph.add_nodes_from([
        PatternModalNodes.AUTHOR_CONCEIVER_NODE,
        PatternModalNodes.EVENT_NODE,
        PatternTokenNodes.ROOT_ADJ_EVENT_TOKEN_NODE
    ])

    pattern_graph.add_edges_from([
        PatternEdges.AUTHOR_CONCEIVER_EVENT_EDGE,
        PatternEdges.EVENT_TOKEN_EDGE
    ])

    node_attrs = [ModalNodeAttrs.modal_node_type,
                  ModalNodeAttrs.special_name,
                  TokenNodeAttrs.upos,
                  TokenNodeAttrs.incoming_dep_rel]
    edge_attrs = [EdgeAttrs.edge_type]

    return Pattern('author_conceiver_event_edge_2', pattern_graph, node_attrs, edge_attrs)
