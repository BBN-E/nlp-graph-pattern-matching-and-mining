import networkx as nx

from constants import NodeTypes, EdgeTypes, \
    BasicNodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    BasicEdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs


class DiGraphMatcherFactory():

    def __init__(self):

        # basic pattern nodes
        self.CONCEIVER_NODE = ('CONCEIVER_NODE', {ModalNodeAttrs.modal_node_type: 'Conceiver'})
        self.EVENT_NODE = ('EVENT_NODE', {ModalNodeAttrs.modal_node_type: 'Event'})
        self.SOURCE_INTRODUCING_PREDICATE = ('SOURCE_INTRODUCING_PREDICATE', {TokenNodeAttrs.upos: 'VERB'})
        self.CONCEIVER_TOKEN = ('CONCEIVER_TOKEN', {})
        self.EVENT_TOKEN = ('EVENT_TOKEN', {})

        # basic pattern edges
        self.CONCEIVER_EVENT_LINK = ('CONCEIVER_NODE', 'EVENT_NODE', {BasicEdgeAttrs.edge_type: 'modal'})  # links conceiver meta-node to event meta-node
        self.CONCEIVER_TOKEN_LINK = ('CONCEIVER_NODE', 'CONCEIVER_TOKEN', {BasicEdgeAttrs.edge_type: 'constituent_token'})  # links conceiver meta-node to conceiver token
        self.EVENT_TOKEN_LINK = ('EVENT_NODE', 'EVENT_TOKEN', {BasicEdgeAttrs.edge_type: 'constituent_token'})  # links event meta-node to event token

        # patterns for matching
        self.patterns = [self.ccomp_pattern]

    def ccomp_pattern(self):

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            self.CONCEIVER_NODE,
            self.EVENT_NODE,
            self.CONCEIVER_TOKEN,
            self.EVENT_TOKEN,
            self.SOURCE_INTRODUCING_PREDICATE
        ])

        pattern.add_edges_from([
            self.CONCEIVER_EVENT_LINK,
            self.CONCEIVER_TOKEN_LINK,
            self.EVENT_TOKEN_LINK,
            ('SOURCE_INTRODUCING_PREDICATE', 'CONCEIVER_TOKEN', {BasicEdgeAttrs.edge_type: 'syntax', SyntaxEdgeAttrs.dep_rel: 'nsubj'}),
            ('SOURCE_INTRODUCING_PREDICATE', 'EVENT_TOKEN', {BasicEdgeAttrs.edge_type: 'syntax', SyntaxEdgeAttrs.dep_rel: 'ccomp'})
        ])

        def node_match(n1, n2):
            a = n1.get(ModalNodeAttrs.modal_node_type, None) == n2.get(ModalNodeAttrs.modal_node_type, None)  # Conceiver, Event
            return a

        def edge_match(e1, e2):
            a = e1[BasicEdgeAttrs.edge_type] == e2[BasicEdgeAttrs.edge_type]  # syntax, modal_dependency, constituent_token
            b = e1.get(SyntaxEdgeAttrs.dep_rel, None) == e2.get(SyntaxEdgeAttrs.dep_rel, None)  # nsubj, ccomp etc.
            return (a and b)

        return pattern, node_match, edge_match
