from ..constants.common.attrs.edge.edge_attrs import EdgeAttrs

from ..constants.special_symbols import DISJUNCTION, EMPTY


def edge_type_match(e1, e2):
    return e1[EdgeAttrs.edge_type] == e2[EdgeAttrs.edge_type]  # syntax, modal_dependency, constituent_token

def edge_attr_match(e1, e2, attr):
    '''
    :param e1: document graph edge
    :param e2: pattern graph edge
    :param attr: edge attribute used to match e1 and e2
    :return: boolean indicating whether the nodes match w.r.t. attr
    '''

    if not edge_type_match(e1, e2):
        return False
    if ((attr in e1) and (attr not in e2)) or \
       ((attr in e2) and (attr not in e1)):
        return True  # if one of the nodes is underspecified w.r.t. attr, then the attrs match
    # return e1.get(attr, None) == e2.get(attr, None)
    return e1.get(attr, EMPTY) in set(e2.get(attr, EMPTY).split(DISJUNCTION))  # permit pattern edge e2 to specify conjunction of attrs, e.g. "nsubj|dobj"

def edge_multiple_attrs_match(*match_fns):

    def edge_multiple_attrs_match_fn(e1, e2):
        return all(match_fn(e1, e2) for match_fn in match_fns)

    return edge_multiple_attrs_match_fn