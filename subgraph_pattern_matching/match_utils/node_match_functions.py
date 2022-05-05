from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs

from constants.special_symbols import DISJUNCTION, EMPTY


def node_type_match(n1, n2):
    '''
    :param n1: document graph node, e.g. {'id': 'based__a118', 'nodeType': 'token', 'text': 'based', 'upos': 'VERB', 'xpos': 'VBN', 'indexInDoc': '2_3_3', 'incomingDepRel': 'amod'}
    :param n2: pattern graph node, e.g. {'nodeType': 'modal', 'modalNodeType': 'Conceiver', 'specialName': 'AUTHOR_NODE'}
    :return: boolean indicating whether the general node types match
    '''

    return n1[NodeAttrs.node_type] == n2[NodeAttrs.node_type]  # modal, token

def node_attr_match(n1, n2, attr):
    '''
    :param n1: document graph node, e.g. {'id': 'based__a118', 'nodeType': 'token', 'text': 'based', 'upos': 'VERB', 'xpos': 'VBN', 'indexInDoc': '2_3_3', 'incomingDepRel': 'amod'}
    :param n2: pattern graph node, e.g. {'nodeType': 'modal', 'modalNodeType': 'Conceiver', 'specialName': 'AUTHOR_NODE'}
    :param attr: node attribute used to match n1 and n2
    :return: boolean indicating whether the nodes match w.r.t. attr
    '''

    if not node_type_match(n1, n2):
        return False
    if ((attr in n1) and (attr not in n2)) or \
       ((attr in n2) and (attr not in n1)):
        return True  # if one of the nodes is underspecified w.r.t. attr, then the attrs match
    # return n1.get(attr, None) == n2.get(attr, None)
    return n1.get(attr, EMPTY) in set(n2.get(attr, EMPTY).split(DISJUNCTION))  # permit pattern node n2 to specify conjunction of attrs, e.g. "VERB|ADJ"

def node_multiple_attrs_match(*match_fns):

    def node_multiple_attrs_match_fn(n1, n2):
        return all(match_fn(n1, n2) for match_fn in match_fns)

    return node_multiple_attrs_match_fn