import networkx as nx

from constants.pattern.node.pattern_modal_nodes import PatternModalNodes
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes
from constants.pattern.edge.pattern_edges import PatternEdges

from match_utils.node_match_functions import node_multiple_attrs_match, node_modal_type_match, node_special_name_match, \
    node_upos_match, node_incoming_dep_rel_match
from match_utils.edge_match_functions import edge_type_match


def author_conceiver_event_edge_pattern_1():
    '''event token is VERB with incoming root relation'''

    pattern = nx.DiGraph()

    pattern.add_nodes_from([
        PatternModalNodes.AUTHOR_CONCEIVER_NODE,
        PatternModalNodes.EVENT_NODE,
        PatternTokenNodes.ROOT_VERB_EVENT_TOKEN_NODE
    ])

    pattern.add_edges_from([
        PatternEdges.AUTHOR_CONCEIVER_EVENT_EDGE,
        PatternEdges.EVENT_TOKEN_EDGE
    ])

    return pattern, node_multiple_attrs_match(node_modal_type_match,
                                              node_special_name_match,
                                              node_upos_match,
                                              node_incoming_dep_rel_match), edge_type_match
