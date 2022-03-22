from constants import *


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
    # TODO is "ε" epsilon char usable in all settings?
    return e1.get(attr, "ε") in set(e2.get(attr, "ε").split("|"))  # permit pattern edge e2 to specify conjunction of attrs, e.g. "nsubj|dobj"

def edge_multiple_attrs_match(*match_fns):

    def edge_multiple_attrs_match_fn(e1, e2):
        return all(match_fn(e1, e2) for match_fn in match_fns)

    return edge_multiple_attrs_match_fn

#######################################################
#######   SINGLE ATTR EDGE MATCHING FUNCTIONS   #######
#######################################################

def edge_modal_relation_match(e1, e2):
    return edge_attr_match(e1, e2, attr=ModalEdgeAttrs.modal_relation)

def edge_syntactic_relation_match(e1, e2):
    return edge_attr_match(e1, e2, attr=SyntaxEdgeAttrs.dep_rel)

def edge_amr_relation_match(e1, e2):
    return edge_attr_match(e1, e2, attr=AMREdgeAttrs.amr_relation)
