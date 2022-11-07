import networkx as nx
from ...constants.pattern.edge.pattern_edges import PatternEdges
from ...constants.pattern.node.pattern_modal_nodes import PatternModalNodes
from ...constants.pattern.node.pattern_token_nodes import PatternTokenNodes


def build_basic_claim_pattern():
    '''build pattern graph with basic relations'''

    pattern = nx.DiGraph()

    pattern.add_nodes_from([
        PatternModalNodes.CONCEIVER_NODE,
        PatternModalNodes.EVENT_NODE,
        PatternTokenNodes.CONCEIVER_TOKEN_NODE,
        PatternTokenNodes.EVENT_TOKEN_NODE
    ])

    pattern.add_edges_from([
        PatternEdges.CONCEIVER_EVENT_EDGE,
        PatternEdges.CONCEIVER_TOKEN_EDGE,
        PatternEdges.EVENT_TOKEN_EDGE
    ])

    return pattern
