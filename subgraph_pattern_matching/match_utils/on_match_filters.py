import networkx

from subgraph_pattern_matching.constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs


def is_ancestor(match_node_id_to_pattern_node_id, document_graph,
                ancestor_id=PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                descendant_id=PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID):
    '''
    :param match_node_id_to_pattern_node_id:  {'a1362': 'CONCEIVER_NODE', 'a1378': 'EVENT_NODE', 'policymakers_a95': 'CONCEIVER_TOKEN', 'epidemic_a91': 'EVENT_TOKEN', 'said_a96': 'SIP', 'need_a81': 'CCOMP_TOKEN'}
    :param document_graph:  networkx graph
    :param ancestor_id:
    :param descendant_id:
    :return:
    '''

    pattern_node_id_to_match_node_id = dict(map(reversed, match_node_id_to_pattern_node_id.items()))
    ancestor_match_id = pattern_node_id_to_match_node_id[ancestor_id]
    descendant_match_id = pattern_node_id_to_match_node_id[descendant_id]

    return ancestor_match_id in networkx.algorithms.dag.ancestors(document_graph, descendant_match_id)