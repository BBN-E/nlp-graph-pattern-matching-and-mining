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

from constants.common.types.node_types import NodeTypes
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.types.edge_types import EdgeTypes
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from constants.common.attrs.edge.modal_edge_attrs import ModalEdgeAttrs


ID_DELIMITER = "_"



class GraphViewer:

    def mdp_node_label (self, G, node):
        if ModalNodeAttrs.special_name in G.nodes[node] and G.nodes[node][ModalNodeAttrs.special_name] != 'Null':
            label = G.nodes[node][ModalNodeAttrs.special_name]
        elif ModalNodeAttrs.modal_node_type in G.nodes[node]:
            label = G.nodes[node][ModalNodeAttrs.modal_node_type]
        else:
            label = node
        return label

    def token_node_label (self, G, node):
        if TokenNodeAttrs.text in G.nodes[node]:
            label = G.nodes[node][TokenNodeAttrs.text]
        else:
            label = node
        return label

    def prepare_mdp_networkx_for_visualization (self, G):
        self.prepare_networkx_for_visualization(G)
        for node in G:
            node_type = G.nodes[node].get(NodeAttrs.node_type, None)
            if node_type == NodeTypes.modal:
                 G.nodes[node]['color'] = "red"
                 G.nodes[node]['label'] = self.mdp_node_label(G,node)
        for edge in G.edges:
            edge_type = G.edges[edge].get(EdgeAttrs.edge_type, None)
            if edge_type == EdgeTypes.modal_constituent_token:
                G.edges[edge]['color'] = "purple"

    def filter_mdp_networkx_by_sentence (self, G, H):
        F = nx.DiGraph()
        # Loop over the nodes from G that are modal nodes
        token_nodes = [x for x in G.nodes if G.nodes[x].get(NodeAttrs.node_type,None) is None]
        sentence_token_nodes = [x for x in token_nodes if x in H.nodes]

        for node in sentence_token_nodes:
            self.add_node_and_ancestors(node, G, F)

        # Loop over the modal nodes in F and add any direct token children from G
        modal_nodes = [x for x in F.nodes if F.nodes[x].get(NodeAttrs.node_type,None) is NodeTypes.modal]
        for node in modal_nodes:
            for edge in G.out_edges(node):
                parent, child = edge
                if G.nodes[child].get(NodeAttrs.node_type,None) is None:
                    F.add_node(child, **G.nodes[child])
                    F.add_edge(parent,child)
        return F

    def add_node_and_ancestors (self, node, Source, Target):
        Target.add_node(node, **Source.nodes[node])
        for edge in Source.in_edges(node):
            parent, child = edge
            self.add_node_and_ancestors (parent, Source, Target)
            Target.add_edge(parent,child,**Source.edges[edge])

    def prepare_sdp_networkx_for_visualization (self, G, root_level=0):
        self.prepare_networkx_for_visualization(G, root_level=root_level)
        for node in G.nodes:
            G.nodes[node]['label'] = self.token_node_label(G,node)

    def prepare_tok_networkx_for_visualization (self, G, root_level=0):
        self.prepare_networkx_for_visualization(G, root_level=root_level)
        # self.invert_node_levels(G)
        for node in G.nodes:
            G.nodes[node]['label'] = self.token_node_label(G,node)

    def prepare_amr_networkx_for_visualization (self, G, root_level=0):
        self.prepare_networkx_for_visualization(G, root_level=root_level)
        for node in G.nodes:
            node_type = G.nodes[node].get(NodeAttrs.node_type, None)
            if node_type == NodeTypes.amr:
                G.nodes[node]['color'] = "orange"
                G.nodes[node]['label'] = self.token_node_label(G,node)
        for edge in G.edges:
            edge_type = G.edges[edge].get(EdgeAttrs.edge_type, None)
            if edge_type == EdgeTypes.amr_aligned_token:
                G.edges[edge]['color'] = "purple"
        # self.invert_node_levels(G)

    def get_max_level(self, G):
        max_level = 0
        for node in G.nodes:
            l = G.nodes[node]['level']
            if l >= max_level:
                max_level = l
        return max_level

    def invert_node_levels(self, G):
        min_level = 1000000
        max_level = 0
        for node in G.nodes:
            l = G.nodes[node]['level']
            if l <= min_level:
                min_level = l
            if l >= max_level:
                max_level = l
        for node in G.nodes:
            l = G.nodes[node]['level']
            G.nodes[node]['level'] = max_level - l + min_level

    def adjust_level(self, G, n):
        for node in G.nodes:
            l = G.nodes[node]['level']
            G.nodes[node]['level'] = l + n

    def prepare_networkx_for_visualization (self, G, root_level=0):
        roots = [x for x in G if len(G.in_edges(x)) == 0]

        for root in roots:
            self.add_level_to_syntactic_dependency_parse (G, root, level=root_level)

        for node in G:
            node_annotation_status = G.nodes[node].get(NodeAttrs.annotated, None)
            if node_annotation_status:
                G.nodes[node]['color'] = "pink"
            elif 'color' not in G.nodes[node]:
                G.nodes[node]['color'] = "blue"

        for edge in G.edges:
            if 'color' not in G.edges[edge]:
                G.edges[edge]['color'] = "blue"


    def add_level_to_syntactic_dependency_parse (self, G, node, level=0):
        G.nodes[node]['level'] = level
        for child in G[node]:
            self.add_level_to_syntactic_dependency_parse (G, child, level=level+1)

    def visualize_networkx_graph(self, G, html_file="graph.html", sentence_text=None):
        if sentence_text is not None:
            net = Network(height='1000px', width='1800px', directed=True, layout=True, heading=sentence_text)
        else:
            net = Network(height='1000px', width='1800px', directed=True, layout=True)
        net.from_nx(G, show_edge_weights=False)

        net.toggle_physics(False)

        # warning: due to bug in pyvis, using show_buttons and set_options together
        # throws an error.
        # net.show_buttons(filter_=['physics'])
        # net.show_buttons(True)
        self.set_node_spacing(net, 160, show_buttons=False)

        # print(html_file)
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

# Support function to build a simple graph of tokens in a sentence.
# Consists of root node with token children in surface string order
def token_sequence_to_networkx(sentence):
    '''
    :param serif_sentence: serif.theory.sentence.Sentence
    :return: networkx.classes.digraph.DiGraph. 
    '''
    G = nx.DiGraph()

    # Root node
    root_id = "Tokens"
    G.add_node(root_id)
    for token in sentence.token_sequence:
        token_id = "{}__{}".format(token.text, token.id)
        G.add_node(token_id)
        G.add_edge(root_id,token_id)

    return G
