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

class GraphViewer:

    def visualize_syntactic_dependency_parse (self, G, i):
        roots = [x for x in G if len(G.in_edges(x)) == 0]
        if len(roots) > 0:
            print(i, roots)
        else:
            print(i, G.nodes)

    def visualize_networkx_graph(self, G, html_file="graph.html"):
        net = Network(height='1000px', width='1800px', directed=True, layout=True)
        net.from_nx(G)
        net.toggle_physics(False)

        # warning: due to bug in pyvis, using show_buttons and set_options together
        # throws an error.
        # net.show_buttons(filter_=['physics'])
        # net.show_buttons(True)
        # self.set_node_spacing(net, 160, show_buttons=False)

        print(html_file)
        net.write_html(html_file)
    

    def serif_doc_to_mdp_nodes (self, serif_doc):
        mtrm_to_node = {}
        mdp_nodes = []
        mtrms = [m for m in serif_doc.modal_temporal_relation_mention_set if re.match("(.*)_modal", m.node.model)]
        for mtrm in mtrms:
            node = MDP_Node(mtrm)
            mdp_nodes.append(node)
            mtrm_to_node[mtrm] = node
        for parent_node in mdp_nodes:
            mtrm = parent_node.mtrm
            for child_mtrm in mtrm.children:
                child_node = mtrm_to_node[child_mtrm]
                child_node.parent = parent_node
                parent_node.children.append(child_node)

        mdp_roots = [x for x in mdp_nodes if x.parent is None]
        return mdp_nodes, mdp_roots


    def serif_doc_to_mdp_graphs_by_sentence (self, serif_doc):
        self.initialize_token_to_mdp_node(serif_doc)

        graphs = []
        for i, sentence in enumerate(serif_doc.sentences):
            G = self.mdp_parse_for_sentence_to_networkx(sentence, root_depth=4)
            graphs.append(G)

        return graphs

    def initialize_token_to_mdp_node (self, serif_doc):
        mdp_nodes, mdp_roots = self.serif_doc_to_mdp_nodes(serif_doc)
        self.token_to_mdp_node = defaultdict(list)
        for mdp_node in mdp_nodes:
            for token in mdp_node.tokens:
                self.token_to_mdp_node[token].append(mdp_node)


    def mdp_parse_for_sentence_to_networkx (self, sentence, root_depth):
        mdp_nodes_in_sentence = set()
        for token in sentence.token_sequence:
            mdp_nodes_in_sentence.update(self.token_to_mdp_node[token])
            for mdp_node in self.token_to_mdp_node[token]:
                parent = mdp_node.parent
                while parent is not None:
                    mdp_nodes_in_sentence.add(parent)
                    parent = parent.parent
        # print("Sentence {} nodes {}".format(
        #     sentence.sent_no, len(mdp_nodes_in_sentence)))
        # print(" ".join([x.label for x in mdp_nodes_in_sentence]))
        G = self.mdp_node_set_to_graph(mdp_nodes_in_sentence)

        return G
        

    def mdp_node_set_to_graph(self, mdp_node_set):
        mdp_roots = [x for x in mdp_node_set if x.parent is None]
        G = nx.DiGraph()
        for root in mdp_roots:
            self.build_mdp_graph(G, root, level=0, mdp_node_set=mdp_node_set)
        return G

    def serif_doc_to_mdp_graph (self, serif_doc):
        mdp_nodes, mdp_roots = self.serif_doc_to_mdp_nodes(serif_doc)

        G = nx.DiGraph()
        for root in mdp_roots:
            self.build_mdp_graph(G, root, level=0)
        return G

    def build_mdp_graph(self, G, mdp_node, level=0, mdp_node_set=None):
        # if mdp_node_set is not None, build a graph using only the nodes
        # that are in mdp_node_set
        # print ("S Len of G {} level {} mdp_node {}".format(
        #     len(G), level, mdp_node.label))

        if mdp_node_set is None or mdp_node in mdp_node_set:
            features = {NodeAttrs.id: mdp_node.label,
                        'level': level,
                        NodeAttrs.color: "red"}
            G.add_node(mdp_node.label, **features)

        for mdp_child in mdp_node.children:
            if mdp_node_set is None or mdp_child in mdp_node_set:
                self.build_mdp_graph(G, mdp_child, level=level+1, mdp_node_set=mdp_node_set)
                G.add_edge(mdp_node.label, mdp_child.label,
                           **{EdgeAttrs.label: mdp_child.mtra.relation_type,
                              EdgeAttrs.color: "red"})
        for token in mdp_node.tokens:
            token_id = self.token_to_id(token)
            token_feats = self.token_to_feats(token, level=level+1)
            # token_feats = self.token_to_feats(token)
            G.add_node(token_id, **token_feats)
            G.add_edge(mdp_node.label, token_id,
                       **{EdgeAttrs.label: "",
                          EdgeAttrs.color : "purple",
                      })

        # print ("E Len of G {} level {} mdp_node {}".format(
        #     len(G), level, mdp_node.label))

    def convert_serif_doc_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        document_level_modal_dependencies_graph = self.modal_dependency_parse_to_networkx(serif_doc)
        root_depth = 4
        sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(s, root_depth=root_depth) for s in serif_doc.sentences]


        # compose into one document-level networkx DiGraph
        G = nx.DiGraph()
        G = nx.algorithms.operators.compose_all(
            [document_level_modal_dependencies_graph] +
            sentence_level_dependency_syntax_graphs[0:1]
        )

        # G1 = nx.algorithms.operators.compose(document_level_modal_dependencies_graph,
        #                                    sentence_level_dependency_syntax_graphs[0])
        # G2 = nx.algorithms.operators.intersection(G1, document_level_modal_dependencies_graph)
        # G3 = nx.algorithms.operators.intersection(G1, sentence_level_dependency_syntax_graphs[0])
        # G4 = nx.algorithms.operators.union([G2,G3])


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

        # This is not clever, but the way that dependency parses of tokens
        # are represented in Serif does not support any kind of tree based
        # traversal of the nodes. This calculates the depth of each token
        # to be used in the graph visualization
        token_depth = {}
        for token in serif_sentence.token_sequence:
            if token.head is None:
                token_depth[token] = root_depth
            elif token.head in token_depth:
                token_depth[token] = token_depth[token.head] + 1
            else:
                depth = root_depth
                parent = token.head
                while parent is not None:
                    parent = parent.head
                    depth += 1
                token_depth[token] = depth

        for token in serif_sentence.token_sequence:
            token_id = self.token_to_id(token)
            token_feats = self.token_to_feats(token, level=token_depth[token])
            G.add_node(token_id, **token_feats)
            

        for token in serif_sentence.token_sequence:
            if token.head == None:
                continue

            parent_id = self.token_to_id(token.head)
            child_id = self.token_to_id(token)

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
