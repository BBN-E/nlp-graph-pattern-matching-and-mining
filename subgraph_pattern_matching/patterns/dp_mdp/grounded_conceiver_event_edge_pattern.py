from .basic_claim_pattern import build_basic_claim_pattern

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs

from patterns.pattern import Pattern

def grounded_conceiver_event_edge_pattern():

    pattern_graph = build_basic_claim_pattern()

    return Pattern('grounded_conciever_event_edge', pattern_graph, [NodeAttrs.node_type], [EdgeAttrs.edge_type])
