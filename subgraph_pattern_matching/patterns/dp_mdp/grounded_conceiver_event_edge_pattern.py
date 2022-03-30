from .basic_claim_pattern import build_basic_claim_pattern

from match_utils.node_match_functions import node_modal_type_match
from match_utils.edge_match_functions import edge_type_match


def grounded_conceiver_event_edge_pattern():

    pattern = build_basic_claim_pattern()

    return pattern, node_modal_type_match, edge_type_match
