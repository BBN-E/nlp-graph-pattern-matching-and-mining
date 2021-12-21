import networkx

def is_ancestor(match_to_pattern, document_graph, ancestor_id='CCOMP_TOKEN', descendant_id='EVENT_TOKEN'):
    '''
    :param match_to_pattern:  {'a1362': 'CONCEIVER_NODE', 'a1378': 'EVENT_NODE', 'policymakers_a95': 'CONCEIVER_TOKEN', 'epidemic_a91': 'EVENT_TOKEN', 'said_a96': 'SIP', 'need_a81': 'CCOMP_TOKEN'}
    :param document_graph:  networkx graph
    :param ancestor_id:
    :param descendant_id:
    :return:
    '''

    pattern_to_match = dict(map(reversed, match_to_pattern.items()))
    ancestor_match_id = pattern_to_match[ancestor_id]
    descendant_match_id = pattern_to_match[descendant_id]

    return ancestor_match_id in networkx.algorithms.dag.ancestors(document_graph, descendant_match_id)