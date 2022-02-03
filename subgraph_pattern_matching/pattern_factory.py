import networkx as nx

from constants import *
from match_utils.node_match_functions import *
from match_utils.edge_match_functions import *


class PatternFactory():


    def __init__(self):

        self.patterns = {'ccomp': self.ccomp_pattern,
                         'relaxed_ccomp': self.relaxed_ccomp_pattern,
                         'relaxed_ccomp_one_hop': self.relaxed_ccomp_one_hop_pattern,
                         'according_to': self.according_to_pattern,
                         'author_conceiver_event_edge_1': self.author_conceiver_event_edge_pattern_1,
                         'author_conceiver_event_edge_2': self.author_conceiver_event_edge_pattern_2,
                         'author_conceiver_event_edge_3': self.author_conceiver_event_edge_pattern_3}#,
                         # 'as_reported_by': self.as_reported_by_pattern}

        self.basic_patterns = {'grounded_conceiver_event_edge': self.grounded_conceiver_event_edge_pattern}


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


    def author_conceiver_event_edge_pattern_1(self):
        '''event token is VERB with incoming root relation'''

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.AUTHOR_CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.ROOT_VERB_EVENT_TOKEN_NODE
        ])

        pattern.add_edges_from([
            PatternEdges.AUTHOR_CONCEIVER_EVENT_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE
        ])

        # return pattern, node_modal_type_and_special_name_and_upos_and_incoming_dep_rel_match, edge_type_match
        return pattern, node_multiple_attrs_match(node_modal_type_match,
                                                  node_special_name_match,
                                                  node_upos_match,
                                                  node_incoming_dep_rel_match), edge_type_match


    def author_conceiver_event_edge_pattern_2(self):
        '''event token is ADJ with incoming root relation'''

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.AUTHOR_CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.ROOT_ADJ_EVENT_TOKEN_NODE
        ])

        pattern.add_edges_from([
            PatternEdges.AUTHOR_CONCEIVER_EVENT_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE
        ])

        # return pattern, node_modal_type_and_special_name_and_upos_and_incoming_dep_rel_match, edge_type_match
        return pattern, node_multiple_attrs_match(node_modal_type_match,
                                                  node_special_name_match,
                                                  node_upos_match,
                                                  node_incoming_dep_rel_match), edge_type_match


    def author_conceiver_event_edge_pattern_3(self):
        '''event token is VERB with incoming ccomp relation'''

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.AUTHOR_CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.CCOMP_VERB_EVENT_TOKEN_NODE
        ])

        pattern.add_edges_from([
            PatternEdges.AUTHOR_CONCEIVER_EVENT_EDGE,
            PatternEdges.EVENT_TOKEN_EDGE
        ])

        # return pattern, node_modal_type_and_special_name_and_upos_and_incoming_dep_rel_match, edge_type_match
        return pattern, node_multiple_attrs_match(node_modal_type_match,
                                                  node_special_name_match,
                                                  node_upos_match,
                                                  node_incoming_dep_rel_match), edge_type_match


    def grounded_conceiver_event_edge_pattern(self):

        pattern = self.build_basic_claim_pattern()

        return pattern, node_modal_type_match, edge_type_match


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

        return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                                  node_upos_match), edge_syntactic_relation_match


    def relaxed_ccomp_one_hop_pattern(self):

        pattern = self.build_basic_claim_pattern()

        pattern.add_nodes_from([
            PatternTokenNodes.SIP_TOKEN_NODE,
            PatternTokenNodes.CCOMP_TOKEN_NODE  # parent of event token
        ])

        pattern.add_edges_from([

            # SIP -(nsubj)-> ConceiverToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),

            # SIP -(ccomp)-> ccompToken
            (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'}),

            # ccompToken -()-> EventToken
            (PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax})
        ])

        return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                                  node_upos_match), edge_syntactic_relation_match


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

        return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                                  node_upos_match), edge_syntactic_relation_match


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

        # return pattern, node_modal_type_and_text_match, edge_syntactic_relation_match
        return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                                  node_text_match), edge_syntactic_relation_match


    def as_reported_by_pattern(self):

        pattern = self.build_basic_claim_pattern()

        pattern.add_nodes_from([
            ('REPORTED_TOKEN_NODE',
             {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.text: 'reported'})
        ])

        pattern.add_nodes_from([
            ('BY_TOKEN_NODE',
             {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.text: 'by'})
        ])

        pattern.add_edges_from([

            # EventToken -(advcl)-> "reported"
            (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID, 'REPORTED_TOKEN_NODE',
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'advcl'}),

            # "reported" -(obl)-> ConceiverToken
            ('REPORTED_TOKEN_NODE', PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'obl'}),

            # ConceiverToken -(case)-> "by"
            (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID, 'BY_TOKEN_NODE',
             {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'case'})
        ])

        return pattern, node_multiple_attrs_match(node_modal_type_match, \
                                                  node_text_match), edge_syntactic_relation_match
