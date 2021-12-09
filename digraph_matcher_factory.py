import networkx as nx


class DiGraphMatcherFactory():

    def __init__(self):

        # basic pattern nodes
        self.CONCEIVER_NODE = ('CONCEIVER_NODE', {'modal_node_type': 'Conceiver'})
        self.EVENT_NODE = ('EVENT_NODE', {'modal_node_type': 'Event'})
        self.SOURCE_INTRODUCING_PREDICATE = ('SOURCE_INTRODUCING_PREDICATE', {'upos': 'VERB'})
        self.CONCEIVER_TOKEN = ('CONCEIVER_TOKEN', {})
        self.EVENT_TOKEN = ('EVENT_TOKEN', {})

        # basic pattern edges
        self.CONCEIVER_EVENT_LINK = ('CONCEIVER_NODE', 'EVENT_NODE', {'edge_type': 'modal_dependency'})  # links conceiver meta-node to event meta-node
        self.CONCEIVER_TOKEN_LINK = ('CONCEIVER_NODE', 'CONCEIVER_TOKEN', {'edge_type': 'constituent_token'})  # links conceiver meta-node to conceiver token
        self.EVENT_TOKEN_LINK = ('EVENT_NODE', 'EVENT_TOKEN', {'edge_type': 'constituent_token'})  # links event meta-node to event token

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
            ('SOURCE_INTRODUCING_PREDICATE', 'CONCEIVER_TOKEN', {'edge_type': 'syntax', 'dep_rel': 'nsubj'}),
            ('SOURCE_INTRODUCING_PREDICATE', 'EVENT_TOKEN', {'edge_type': 'syntax', 'dep_rel': 'ccomp'})
        ])

        def node_match(n1, n2):
            a = n1.get('modal_node_type', None) == n2.get('modal_node_type', None)  # Conceiver, Event
            return a

        def edge_match(e1, e2):
            a = e1['edge_type'] == e2['edge_type']  # syntax, modal_dependency, constituent_token
            b = e1.get('dep_rel', None) == e2.get('dep_rel', None)  # nsubj, ccomp etc.
            # c = e1.get('modal_relation', None) == e2.get('modal_relation', None)  # pos, neg, pn
            return (a and b)

        return pattern, node_match, edge_match
