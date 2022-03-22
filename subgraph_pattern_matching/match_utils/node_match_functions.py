from constants import *


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
    # TODO is "ε" epsilon char usable in all settings?
    return n1.get(attr, "ε") in set(n2.get(attr, "ε").split("|"))  # permit pattern node n2 to specify conjunction of attrs, e.g. "VERB|ADJ"


def node_multiple_attrs_match(*match_fns):

    def node_multiple_attrs_match_fn(n1, n2):
        return all(match_fn(n1, n2) for match_fn in match_fns)

    return node_multiple_attrs_match_fn


#######################################################
#######   SINGLE ATTR NODE MATCHING FUNCTIONS   #######
#######################################################

def node_modal_type_match(n1, n2):
    return node_attr_match(n1, n2, attr=ModalNodeAttrs.modal_node_type)

def node_special_name_match(n1, n2):
    if not node_modal_type_match(n1, n2):
        return False
    return node_attr_match(n1, n2, attr=ModalNodeAttrs.special_name)

def node_upos_match(n1, n2):
    return node_attr_match(n1, n2, attr=TokenNodeAttrs.upos)

def node_incoming_dep_rel_match(n1, n2):
    return node_attr_match(n1, n2, attr=TokenNodeAttrs.incoming_dep_rel)

def node_text_match(n1, n2):
    return node_attr_match(n1, n2, attr=TokenNodeAttrs.text)

def node_amr_match(n1, n2):
    return node_attr_match(n1, n2, attr=AMRNodeAttrs.content)