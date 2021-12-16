import networkx as nx

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs, \
    PatternTokenNodes, PatternModalNodes, PatternEdges, \
    PatternTokenNodeIDs, PatternModalNodeIDs

from node_match_functions import node_type_match, node_modal_type_match, node_upos_match, node_modal_type_and_upos_match
from edge_match_functions import edge_type_match, edge_syntactic_relation_match


class DiGraphMatcherFactory():


    def __init__(self):
        self.patterns = [self.ccomp_pattern, self.relaxed_ccomp_pattern]


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

        return pattern, node_modal_type_and_upos_match, edge_syntactic_relation_match


    def relaxed_ccomp_pattern(self):

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.CONCEIVER_TOKEN_NODE,
            PatternTokenNodes.EVENT_TOKEN_NODE,
            PatternTokenNodes.SIP_TOKEN_NODE,
            PatternTokenNodes.CCOMP_TOKEN_NODE  # may be the same as event token
        ])

        pattern.add_edges_from([

            PatternEdges.CONCEIVER_EVENT_EDGE,
            PatternEdges.CONCEIVER_TOKEN_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE,

            # SIP -(nsubj)-> ConceiverToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

            # SIP -(ccomp)-> ccompToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'})
        ])

        return pattern, node_modal_type_and_upos_match, edge_syntactic_relation_match

    #
    # def according_to_pattern(self):
    #
    #     pattern = nx.DiGraph()
    #
    #     pattern.add_nodes_from([
    #         PatternModalNodes.CONCEIVER_NODE,
    #         PatternModalNodes.EVENT_NODE,
    #         PatternTokenNodes.CONCEIVER_TOKEN_NODE,
    #         PatternTokenNodes.EVENT_TOKEN_NODE,
    #         ({'text': 'according'})
    #     ])
    #
    #     pattern.add_edges_from([
    #
    #         PatternEdges.CONCEIVER_EVENT_EDGE,
    #         PatternEdges.CONCEIVER_TOKEN_EDGE,
    #         PatternEdges.EVENT_TOKEN_EDGE,
    #
    #         # EventToken -(obl)-> ConceiverToken
    #         (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
    #          {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'obl'}),
    #
    #         # ConceiverToken -(case)-> "according"
    #         (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
    #          {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'case'})
    #     ])
    #
    #     def node_match(n1, n2):
    #         a = n1.get(ModalNodeAttrs.modal_node_type, None) == n2.get(ModalNodeAttrs.modal_node_type, None)  # Conceiver, Event
    #         return a
    #
    #     def edge_match(e1, e2):
    #         a = e1[EdgeAttrs.edge_type] == e2[EdgeAttrs.edge_type]  # syntax, modal_dependency, constituent_token
    #         b = e1.get(SyntaxEdgeAttrs.dep_rel, None) == e2.get(SyntaxEdgeAttrs.dep_rel, None)  # nsubj, ccomp etc.
    #         return (a and b)
    #
    #     return pattern, node_match, edge_match
