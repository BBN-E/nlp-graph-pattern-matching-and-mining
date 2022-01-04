from constants import *


def edge_type_match(e1, e2):
    return e1[EdgeAttrs.edge_type] == e2[EdgeAttrs.edge_type]  # syntax, modal_dependency, constituent_token

def edge_modal_relation_match(e1, e2):
    if not edge_type_match(e1, e2):
        return False
    if ((ModalEdgeAttrs.modal_relation in e1) and (ModalEdgeAttrs.modal_relation not in e2)) or \
       ((ModalEdgeAttrs.modal_relation in e2) and (ModalEdgeAttrs.modal_relation not in e1)):
        return True  # if one of the edges is underspecified in modal relation, then the modal relations match
    return e1.get(ModalEdgeAttrs.modal_relation, None) == e2.get(ModalEdgeAttrs.modal_relation, None)  # nsubj, ccomp etc.

def edge_syntactic_relation_match(e1, e2):
    if not edge_type_match(e1, e2):
        return False
    if ((SyntaxEdgeAttrs.dep_rel in e1) and (SyntaxEdgeAttrs.dep_rel not in e2)) or \
       ((SyntaxEdgeAttrs.dep_rel in e2) and (SyntaxEdgeAttrs.dep_rel not in e1)):
        return True  # if one of the edges is underspecified in dep_rel, then the dep_rel match
    return e1.get(SyntaxEdgeAttrs.dep_rel, None) == e2.get(SyntaxEdgeAttrs.dep_rel, None)  # nsubj, ccomp etc.

def edge_modal_and_syntactic_relation_match(e1, e2):
    return edge_modal_relation_match(e1, e2) and edge_syntactic_relation_match(e1, e2)