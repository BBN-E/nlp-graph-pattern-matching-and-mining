from constants import *


def node_type_match(n1, n2):
    return n1[NodeAttrs.node_type] == n2[NodeAttrs.node_type]  # modal, token

def node_modal_type_match(n1, n2):
    if not node_type_match(n1, n2):
        return False
    return n1.get(ModalNodeAttrs.modal_node_type, None) == n2.get(ModalNodeAttrs.modal_node_type, None)  # Conceiver, Event

def node_upos_match(n1, n2):
    if not node_type_match(n1, n2):
        return False
    if ((TokenNodeAttrs.upos in n1) and (TokenNodeAttrs.upos not in n2)) or \
       ((TokenNodeAttrs.upos in n2) and (TokenNodeAttrs.upos not in n1)):
        return True  # if one of the nodes is underspecified in pos, then the pos match
    return n1.get(TokenNodeAttrs.upos, None) == n2.get(TokenNodeAttrs.upos, None)  # VERB, NOUN, ADJ etc.

def node_text_match(n1, n2):
    if not node_upos_match(n1, n2):
        return False
    if ((TokenNodeAttrs.text in n1) and (TokenNodeAttrs.text not in n2)) or \
       ((TokenNodeAttrs.text in n2) and (TokenNodeAttrs.text not in n1)):
        return True  # if one of the nodes is underspecified in text, then the text match
    return n1.get(TokenNodeAttrs.text, None) == n2.get(TokenNodeAttrs.text, None)

def node_modal_type_and_upos_match(n1, n2):
    return node_modal_type_match(n1, n2) and node_upos_match(n1, n2)

def node_modal_type_and_text_match(n1, n2):
    return node_modal_type_match(n1, n2) and node_text_match(n1, n2)
