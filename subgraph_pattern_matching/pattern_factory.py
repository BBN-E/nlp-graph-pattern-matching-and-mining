import networkx as nx

# pattern constants
from constants.pattern.id.pattern_node_ids import PatternNodeIDs
from constants.pattern.id.pattern_modal_node_ids import PatternModalNodeIDs
from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs

from constants.pattern.node.pattern_nodes import PatternNodes
from constants.pattern.node.pattern_amr_nodes import PatternAMRNodes
from constants.pattern.node.pattern_modal_nodes import PatternModalNodes
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes

from constants.pattern.edge.pattern_edges import PatternEdges
from constants.pattern.node.pattern_nodes import PatternNodes
from constants.pattern.node.pattern_amr_nodes import PatternAMRNodes
from constants.pattern.node.pattern_modal_nodes import PatternModalNodes
from constants.pattern.node.pattern_token_nodes import PatternTokenNodes

# common constants
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.amr_aligned_token_edge_attrs import AMRAlignedTokenEdgeAttrs
from constants.common.attrs.edge.amr_edge_attrs import AMREdgeAttrs
from constants.common.attrs.edge.modal_constitutent_token_edge_attrs import ModalConstituentTokenEdgeAttrs
from constants.common.attrs.edge.modal_edge_attrs import ModalEdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs

from constants.common.types.edge_types import EdgeTypes
from constants.common.types.node_types import NodeTypes


from match_utils.node_match_functions import *
from match_utils.edge_match_functions import *


class PatternFactory():

    def __init__(self):

        self.patterns = {'ccomp': self.ccomp_pattern,
                         'relaxed_ccomp': self.relaxed_ccomp_pattern,
                         'relaxed_ccomp_one_hop': self.relaxed_ccomp_one_hop_pattern,
                         'according_to': self.according_to_pattern,
                         # 'author_conceiver_event_edge_0': self.author_conceiver_event_edge_pattern_0,
                         'author_conceiver_event_edge_1': self.author_conceiver_event_edge_pattern_1,
                         'author_conceiver_event_edge_2': self.author_conceiver_event_edge_pattern_2,
                         'author_conceiver_event_edge_3': self.author_conceiver_event_edge_pattern_3,
                         'as_reported_by': self.as_reported_by_pattern}

        self.basic_patterns = {'grounded_conceiver_event_edge': self.grounded_conceiver_event_edge_pattern}

        # self.amr_patterns = self.create_propbank_frames_patterns()
        self.amr_patterns = {'person_says_x_pattern': self.person_says_x_pattern}

    ######################################################
    #                MDP + DP Patterns                   #
    ######################################################

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

    ######################################################

    def grounded_conceiver_event_edge_pattern(self):

        pattern = self.build_basic_claim_pattern()

        return pattern, node_modal_type_match, edge_type_match

    ######################################################

    def author_conceiver_event_edge_pattern_0(self):
        '''event token is VERB|ADJ with incoming root relation'''

        pattern = nx.DiGraph()

        pattern.add_nodes_from([
            PatternModalNodes.AUTHOR_CONCEIVER_NODE,
            PatternModalNodes.EVENT_NODE,
            PatternTokenNodes.ROOT_EVENT_TOKEN_NODE
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

    ######################################################

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

    ######################################################

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
             {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.text: 'reported|stated'})
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

    ######################################################
    #                   AMR Patterns                     #
    ######################################################

    def create_propbank_frames_patterns(self):

        from utils.load_propbank_to_xpo_mapping import load_propbank_to_xpo_mapping
        propbank_to_xpo = load_propbank_to_xpo_mapping()

        pb_frame_to_nx_pattern = dict()
        for pb_frame in propbank_to_xpo.keys():
            G = nx.DiGraph()
            G.add_node(pb_frame, **{NodeAttrs.node_type: NodeTypes.amr,
                                    AMRNodeAttrs.content: pb_frame})
            pb_frame_to_nx_pattern[pb_frame] = lambda: (G, node_amr_match, None)

        return pb_frame_to_nx_pattern

    def person_says_x_pattern(self):
        '''
        1) "John says that Mary is sad."
        2) "Mary is sad, according to John."

        Both (1) and (2) receive identical AMR parses with "say-01" at the root, and an :arg0 of type "person"
        '''

        G = nx.DiGraph()

        G.add_node("say-01", **{NodeAttrs.node_type: NodeTypes.amr,
                                AMRNodeAttrs.content: "say-01"})
        G.add_node("person", **{NodeAttrs.node_type: NodeTypes.amr,
                                AMRNodeAttrs.content: "person"})

        G.add_edge("say-01", "person", **{EdgeAttrs.edge_type: EdgeTypes.amr,
                                          AMREdgeAttrs.amr_relation: ":arg0"})

        return G, node_amr_match, edge_amr_relation_match