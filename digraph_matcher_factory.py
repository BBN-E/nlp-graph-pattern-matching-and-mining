import networkx as nx

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs, \
    PatternTokenNodes, PatternModalNodes, PatternEdges, \
    PatternTokenNodeIDs, PatternModalNodeIDs

from node_match_functions import node_type_match, node_modal_type_match, node_upos_match, \
    node_modal_type_and_upos_match, node_modal_type_and_text_match
from edge_match_functions import edge_type_match, edge_syntactic_relation_match


class DiGraphMatcherFactory():


    def __init__(self):

        self.patterns = {'ccomp': self.ccomp_pattern,
                         'relaxed_ccomp': self.relaxed_ccomp_pattern,
                         'according_to': self.according_to_pattern}


    def build_basic_claim_pattern(self):
        '''build pattern graph with basic relations'''

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.CONCEIVER_TOKEN_NODE,
            PatternTokenNodes.EVENT_TOKEN_NODE
        ])

        pattern.add_edges_from([
            PatternEdges.CONCEIVER_EVENT_EDGE,
            PatternEdges.CONCEIVER_TOKEN_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE
        ])

        return pattern


    def ccomp_pattern(self):

        pattern = self.build_basic_claim_pattern()

        pattern.add_nodes_from([
            PatternTokenNodes.SIP_TOKEN_NODE
        ])

        pattern.add_edges_from([

            # SIP -(nsubj)-> ConceiverToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

            # SIP -(ccomp)-> EventToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'})
        ])

        return pattern, node_modal_type_and_upos_match, edge_syntactic_relation_match


    def relaxed_ccomp_pattern(self):

        pattern = self.build_basic_claim_pattern()

        pattern.add_nodes_from([
            PatternTokenNodes.SIP_TOKEN_NODE,
            PatternTokenNodes.CCOMP_TOKEN_NODE  # may be the same as event token  # TODO results in the EVENT_TOKEN 1-hop below CCOMP_TOKEN not being matched
        ])

        pattern.add_edges_from([

            # SIP -(nsubj)-> ConceiverToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

            # TODO results in the EVENT_TOKEN 1-hop below CCOMP_TOKEN not being matched
            # SIP -(ccomp)-> ccompToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'})
        ])

        return pattern, node_modal_type_and_upos_match, edge_syntactic_relation_match


    def according_to_pattern(self):

        pattern = self.build_basic_claim_pattern()

        pattern.add_nodes_from([
            ('ACCORDING_TOKEN_NODE',
             {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.text: 'according'})
        ])

        pattern.add_edges_from([

            # EventToken -(obl)-> ConceiverToken
            (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'obl'}),

            # ConceiverToken -(case)-> "according"
            (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID, 'ACCORDING_TOKEN_NODE',
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'case'})
        ])

        return pattern, node_modal_type_and_text_match, edge_syntactic_relation_match
