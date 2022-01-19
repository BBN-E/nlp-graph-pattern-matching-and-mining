import re
import json
from collections import defaultdict
import networkx as nx
# import matplotlib.pyplot as plt
from pyvis.network import Network

import serifxml3

from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs
from verify_graph_compliance import verify_graph_compliance

ID_DELIMITER = "_"

class MDP_Node:
    def __init__ (self, mtrm):
        self.mtrm = mtrm
        self.mtra = mtrm.node
        self.children = []
        self.parent = None
        self.tokens = self.mtrm_to_tokens()
        self.sentence = None
        if len(self.tokens) > 0:
            self.sentence = self.tokens[0].sentence
        if type(self.mtra.value) == str:
            self.label = ID_DELIMITER.join(
                [self.mtra.id, self.mtra.value])
        elif self.sentence is None:
            self.label = ID_DELIMITER.join(
                [self.mtra.id, self.mtra.modal_temporal_node_type])
        else:
            self.label = ID_DELIMITER.join(
                [self.mtra.id, self.mtra.modal_temporal_node_type])

    def mtrm_to_tokens (self):
        value_type = type(self.mtra.value)

        if value_type == str:
            tokens = []

        elif value_type == EventMention:
            event_mention = self.mtra.value
            if event_mention.anchor_node is not None:
                sentence = event_mention.sentence
                start_token = event_mention.anchor_node.start_token
                end_token = event_mention.anchor_node.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

            else:
                sentence = event_mention.sentence
                start_token_index = event_mention.semantic_phrase_start
                end_token_index = event_mention.semantic_phrase_end
                tokens = sentence.token_sequence[start_token_index:end_token_index+1]

        elif value_type == Mention:
            mention = self.mtra.value
            if mention.syn_node is not None:
                sentence = mention.sentence
                start_token = mention.syn_node.start_token
                end_token = mention.syn_node.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

            else:
                sentence = mention.sentence
                start_token = mention.start_token
                end_token = mention.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

        elif value_type == ValueMention:
            value_mention = self.mtra.value

            sentence = value_mention.sentence
            start_token = value_mention.start_token
            end_token = value_mention.end_token
            tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

        else:
            raise TypeError

        return tokens
    

class GraphBuilder():

    def __init__(self):
        pass

    def serif_doc_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        # make sure all the tokens in the document exist beforehand to prevent creating empty token nodes
        # when adding constituent_token edges
        disconnected_tokens_digraph = nx.DiGraph()
        for sentence in serif_doc.sentences:
            for token in sentence.token_sequence:
                token_feats = self.token_to_feats(token)
                token_id = token_feats['id']
                disconnected_tokens_digraph.add_node(token_id, **token_feats)

        document_level_modal_dependencies_graph = self.modal_dependency_parse_to_networkx(serif_doc)
        root_depth = 4
        sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(s, root_depth=root_depth) for s in serif_doc.sentences]


        # compose into one document-level networkx DiGraph
        G = nx.algorithms.operators.compose_all([disconnected_tokens_digraph] + \
                                                [document_level_modal_dependencies_graph] + \
                                                sentence_level_dependency_syntax_graphs)

        assert nx.algorithms.dag.is_directed_acyclic_graph(G)
        verify_graph_compliance(G)

        return G

    def modal_dependency_parse_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        if serif_doc.modal_temporal_relation_mention_set is None:
            return G

        mtrm_list = [m for m in serif_doc.modal_temporal_relation_mention_set if re.match("(.*)_modal", m.node.model)]

        mtrm_depth = {}
        for mtrm in mtrm_list:
            self.set_mtrm_depth(mtrm, mtrm_depth, depth=0)

        mtrm_tokens = {}
        mtrm_modal_relations = {}

        for mtrm in mtrm_list:
            mtrm_id = self.modal_temporal_relation_mention_to_id(mtrm)
            mtrm_features = self.modal_temporal_relation_mention_to_feats(mtrm)
            mtrm_features_arg = {k:v for k,v in mtrm_features.items() if type(v)==str}
            mtrm_features_arg['level'] = mtrm_depth[mtrm]
            G.add_node(mtrm_id, **mtrm_features_arg)

            mtrm_tokens[mtrm] = mtrm_features['tokens']
            mtrm_modal_relations[mtrm] = mtrm_features[ModalNodeAttrs.modal_relation]

            for token in mtrm_features['tokens']:
                token_id = self.token_to_id(token)
                token_feats = self.token_to_feats(token)
                token_feats['level'] = mtrm_depth[mtrm] + 1
                G.add_node(token_id, **token_feats)

        for parent_mtrm in mtrm_list:
            for child_mtrm in parent_mtrm.children:
                G.add_edge(self.modal_temporal_relation_mention_to_id(parent_mtrm),
                           self.modal_temporal_relation_mention_to_id(child_mtrm),
                           **{EdgeAttrs.label: mtrm_modal_relations[child_mtrm],
                              EdgeAttrs.edge_type: EdgeTypes.constituent_token,
                              EdgeAttrs.color : "red"})
            for token in mtrm_tokens[parent_mtrm]:
                G.add_edge(self.modal_temporal_relation_mention_to_id(parent_mtrm),
                           self.token_to_id(token),
                           **{EdgeAttrs.label: "",
                              ModalEdgeAttrs.modal_relation: mtrm_modal_relations[parent_mtrm],
                              EdgeAttrs.edge_type: EdgeTypes.modal,
                              EdgeAttrs.color : "purple",
                          })


        return G

    def set_mtrm_depth(self, mtrm, mtrm_depth, depth=0):
        if mtrm not in mtrm_depth:
            mtrm_depth[mtrm] = depth
        for child in mtrm.children:
            self.set_mtrm_depth(child, mtrm_depth, mtrm_depth[mtrm]+1)

    def syntactic_dependency_parse_to_networkx(self, serif_sentence, root_depth=0):
        '''
        :param serif_sentence: serif.theory.sentence.Sentence
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        # Add all nodes first, to handle case where sentence consists of
        # a single token.

        for i, token in enumerate(serif_sentence.token_sequence):
            child_feats = self.token_to_feats(token)
            child_id = child_feats['id']
            G.add_node(child_id, **child_feats)

        for i, token in enumerate(serif_sentence.token_sequence):
            if token.head == None:  # root token, can't be child
                assert token.dep_rel == 'root'
                continue

            child_feats = self.token_to_feats(token)
            child_id = child_feats['id']
            parent_feats = self.token_to_feats(token.head)
            parent_id = parent_feats['id']

            G.add_edge(parent_id, child_id,
                       **{EdgeAttrs.label: token.dep_rel,
                          SyntaxEdgeAttrs.dep_rel: token.dep_rel,
                          EdgeAttrs.edge_type: EdgeTypes.syntax})
            
        return G

    def token_to_id(self, token):
        sentence = token.sentence
        sent_no = sentence.sent_no
        return ID_DELIMITER.join([token.id, token.text])

    def token_to_feats(self, token, level=None):
        '''
        :type token: serif.theory.token.Token
        :return: dict
        '''

        token_id = self.token_to_id(token)
        feats = {NodeAttrs.id: token_id,
                 NodeAttrs.node_type: NodeTypes.token,
                 NodeAttrs.color : "blue",
                 TokenNodeAttrs.text: token.text,
                 TokenNodeAttrs.upos: token.upos,
                 TokenNodeAttrs.xpos: token.xpos,
                 TokenNodeAttrs.index_in_doc: "_".join([str(token.sentence.sent_no), str(token.index()), str(token.index())])}
        if level is not None:
            feats['level'] = level

        return feats

    def modal_temporal_relation_mention_to_id(self, mtrm):
        mtra = mtrm.node
        value_type = type(mtra.value)
        if value_type == str:
            label = mtra.value
        else:
            label = mtra.modal_temporal_node_type

        

        return ID_DELIMITER.join([mtra.id, label])

    def modal_temporal_relation_mention_to_feats(self, mtrm):
        '''
        :param mtrm: serif.theory.modal_temporal_relation_mention.ModalTemporalRelationMention
        :return: dict
        '''

        mtra = mtrm.node  # modal_temporal_relation_argument

        special_name = None
        mention = None
        event_mention = None
        value_mention = None
        sentence = None
        tokens = []

        value_type = type(mtra.value)
        if value_type == str:
            special_name = mtra.value

        elif value_type == EventMention:
            event_mention = mtra.value
            if event_mention.anchor_node is not None:
                sentence = event_mention.sentence
                start_token = event_mention.anchor_node.start_token
                end_token = event_mention.anchor_node.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

            else:
                sentence = event_mention.sentence
                start_token_index = event_mention.semantic_phrase_start
                end_token_index = event_mention.semantic_phrase_end
                tokens = sentence.token_sequence[start_token_index:end_token_index+1]

        elif value_type == Mention:
            mention = mtra.value
            if mention.syn_node is not None:
                sentence = mention.sentence
                start_token = mention.syn_node.start_token
                end_token = mention.syn_node.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

            else:
                sentence = mention.sentence
                start_token = mention.start_token
                end_token = mention.end_token
                tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

        elif value_type == ValueMention:
            value_mention = mtra.value

            sentence = value_mention.sentence
            start_token = value_mention.start_token
            end_token = value_mention.end_token
            tokens = sentence.token_sequence[start_token.index():end_token.index()+1]

        else:
            raise TypeError

        feats = {

            NodeAttrs.id: self.modal_temporal_relation_mention_to_id(mtrm),
            NodeAttrs.node_type: NodeTypes.modal,
            NodeAttrs.color : "red",

            ModalNodeAttrs.special_name: special_name,
            ModalNodeAttrs.mention: mention,
            ModalNodeAttrs.event_mention: event_mention,
            ModalNodeAttrs.value_mention: value_mention,

            ModalNodeAttrs.sentence: sentence,
            ModalNodeAttrs.tokens: tokens,

            ModalNodeAttrs.modal_node_type: mtra.modal_temporal_node_type,  # Event, Conceiver
            ModalNodeAttrs.modal_relation: mtra.relation_type  # pos, neg, pn
        }

        return feats

    def visualize_networkx_graph(self, G, html_file="graph.html"):
        # net = Network('750px', '5000px', directed=True)
        net = Network(height='1000px', width='1800px', directed=True, layout=True)
        net.from_nx(G)
        net.toggle_physics(False)

        # warning: due to bug in pyvis, using show_buttons and set_options together
        # throws an error.
        # net.show_buttons(filter_=['physics'])
        # net.show_buttons(True)
        # self.set_node_spacing(net, 160, show_buttons=False)

        # net.show(html_file)
        print(html_file)
        net.write_html(html_file)

    def set_node_spacing(self, net, node_spacing, show_buttons=False):
        json_dict = {
            # warning: due to bug in pyvis, you must include configure
            "configure": {
                "enabled": show_buttons
            },
            "layout": {
                "hierarchical": {
                    "enabled": True,
                    "nodeSpacing": node_spacing,
                    # "treeSpacing": 290
                }
            },
            "physics": {
                "enabled": False,
                "hierarchicalRepulsion": {
                    "centralGravity": 0
                },
                "minVelocity": 0.75,
                "solver": "hierarchicalRepulsion"
            }
        }
        json_dump = json.dumps(json_dict)
        new_options = "var options = {}".format(json_dump)
        # print(new_options)
        net.set_options(new_options)
