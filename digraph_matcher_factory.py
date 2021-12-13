import networkx as nx

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs, \
    PatternTokenNodes, PatternModalNodes, PatternEdges, \
    PatternTokenNodeIDs, PatternModalNodeIDs

class DiGraphMatcherFactory():

    def __init__(self):

        # patterns for matching
        self.patterns = [self.ccomp_pattern]

    def ccomp_pattern(self):

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.CONCEIVER_TOKEN_NODE,
            PatternTokenNodes.EVENT_TOKEN_NODE,
            PatternTokenNodes.SIP_TOKEN_NODE
        ])

        pattern.add_edges_from([

            PatternEdges.CONCEIVER_EVENT_EDGE,
            PatternEdges.CONCEIVER_TOKEN_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE,

            # SIP -(nsubj)-> ConceiverToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

            # SIP -(ccomp)-> EventToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'})
        ])

        def node_match(n1, n2):
            a = n1.get(ModalNodeAttrs.modal_node_type, None) == n2.get(ModalNodeAttrs.modal_node_type, None)  # Conceiver, Event
            return a

        def edge_match(e1, e2):
            a = e1[EdgeAttrs.edge_type] == e2[EdgeAttrs.edge_type]  # syntax, modal_dependency, constituent_token
            b = e1.get(SyntaxEdgeAttrs.dep_rel, None) == e2.get(SyntaxEdgeAttrs.dep_rel, None)  # nsubj, ccomp etc.
            return (a and b)

        return pattern, node_match, edge_match
