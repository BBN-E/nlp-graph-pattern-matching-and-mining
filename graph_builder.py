import re
import networkx as nx

import serifxml3

from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs


class GraphBuilder():

    def __init__(self):
        pass

    def convert_serif_doc_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        document_level_modal_dependencies_graph = self.modal_dependency_parse_to_networkx(serif_doc)
        sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(s) for s in serif_doc.sentences]
        # sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(serif_doc.sentences[17])]

        # compose into one document-level networkx DiGraph
        G = nx.algorithms.operators.compose_all([document_level_modal_dependencies_graph] + \
                                                sentence_level_dependency_syntax_graphs)
        return G

    def modal_dependency_parse_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        if serif_doc.modal_temporal_relation_mention_set is None:
            return

        mtrm_list = [m for m in serif_doc.modal_temporal_relation_mention_set if re.match("(.*)_modal", m.node.model)]

        for parent_mtrm in mtrm_list:

            # create parent node
            parent_mtrm_feats = self.modal_temporal_relation_mention_to_feats(parent_mtrm)
            parent_mtrm_id = parent_mtrm_feats['id']
            G.add_node(parent_mtrm_id, **{k:v for k,v in parent_mtrm_feats.items() if type(v)==str})

            # connect parent node to all of its tokens
            parent_token_ids = [self.token_to_feats(t)['id'] for t in parent_mtrm_feats['tokens']]
            G.add_edges_from(list(map(lambda t: (parent_mtrm_id, t), parent_token_ids)),
                             **{EdgeAttrs.label: EdgeTypes.constituent_token,
                                EdgeAttrs.edge_type: EdgeTypes.constituent_token})

            for child_mtrm in parent_mtrm.children:

                # create child node
                child_mtrm_feats = self.modal_temporal_relation_mention_to_feats(child_mtrm)
                child_mtrm_id = child_mtrm_feats['id']
                G.add_node(child_mtrm_id, **{k:v for k,v in child_mtrm_feats.items() if type(v)==str})

                # connect child node to all of its tokens
                child_token_ids = [self.token_to_feats(t)['id'] for t in child_mtrm_feats['tokens']]
                G.add_edges_from(list(map(lambda t: (child_mtrm_id, t), child_token_ids)),
                                 **{EdgeAttrs.label: EdgeTypes.constituent_token,
                                    EdgeAttrs.edge_type: EdgeTypes.constituent_token})

                # modal dependency edge between parent and child nodes
                G.add_edge(parent_mtrm_id, child_mtrm_id,
                           **{EdgeAttrs.label: child_mtrm_feats[ModalNodeAttrs.modal_relation],
                              ModalEdgeAttrs.modal_relation: child_mtrm_feats[ModalNodeAttrs.modal_relation],
                              EdgeAttrs.edge_type: EdgeTypes.modal})

        return G

    def syntactic_dependency_parse_to_networkx(self, serif_sentence):
        '''
        :param serif_sentence: serif.theory.sentence.Sentence
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        for token in serif_sentence.token_sequence:

            if token.head == None:  # root token, can't be child
                assert token.dep_rel == 'root'
                continue

            parent_feats = self.token_to_feats(token.head)
            parent_id = parent_feats['id']
            G.add_node(parent_id, **parent_feats)

            child_feats = self.token_to_feats(token)
            child_id = child_feats['id']
            G.add_node(child_id, **child_feats)

            G.add_edge(parent_id, child_id,
                       **{EdgeAttrs.label: token.dep_rel,
                          SyntaxEdgeAttrs.dep_rel: token.dep_rel,
                          EdgeAttrs.edge_type: EdgeTypes.syntax})

        return G

    def token_to_feats(self, token):
        '''
        :type token: serif.theory.token.Token
        :return: dict
        '''

        feats = {NodeAttrs.id: token.text + "_" + token.id,
                 TokenNodeAttrs.text: token.text,
                 TokenNodeAttrs.upos: token.upos,
                 TokenNodeAttrs.xpos: token.xpos,
                 TokenNodeAttrs.index_in_doc: "_".join([str(token.sentence.sent_no), str(token.index()), str(token.index())])}

        return feats

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

            NodeAttrs.id: mtra.id,  # TODO or mtrm.id + mtra.id ?

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

    def visualize_networkx_graph(self, G):
        from pyvis.network import Network
        net = Network('750px', '1500px')
        net.from_nx(G)
        net.show("graph.html")
