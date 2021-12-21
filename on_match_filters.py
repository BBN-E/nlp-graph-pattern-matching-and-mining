import networkx

def is_ancestor(isomorphism_dict, document_graph, ancestor_id='CCOMP_TOKEN', descendant_id='EVENT_TOKEN'):
    '''
    :param isomorphism_dict:  {'a1362': 'CONCEIVER_NODE', 'a1378': 'EVENT_NODE', 'policymakers_a95': 'CONCEIVER_TOKEN', 'epidemic_a91': 'EVENT_TOKEN', 'said_a96': 'SIP', 'need_a81': 'CCOMP_TOKEN'}
    :param document_graph:  networkx graph
    :param ancestor_id:
    :param descendant_id:
    :return:
    '''

    pattern_id_to_match_id = dict(map(reversed, isomorphism_dict.items()))
    ancestor_match_id = pattern_id_to_match_id[ancestor_id]
    descendant_match_id = pattern_id_to_match_id[descendant_id]

    return ancestor_match_id in networkx.algorithms.dag.ancestors(document_graph, descendant_match_id)