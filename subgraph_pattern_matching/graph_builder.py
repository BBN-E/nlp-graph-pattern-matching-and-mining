import re
import json
import networkx as nx
import logging

import serifxml3

from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from constants import *
from verify_graph_compliance import verify_graph_compliance


logging.basicConfig(level=logging.INFO)


ID_DELIMITER = "__"

class GraphBuilder():

    def __init__(self):
        pass

    def serif_doc_to_networkx(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        # make sure all the tokens in the document exist beforehand to prevent creating empty token nodes
        # when adding modal_constituent_token edges
        disconnected_tokens_digraph = nx.DiGraph()
        for sentence in serif_doc.sentences:
            for token in sentence.token_sequence:
                token_feats = self.token_to_feats(token)
                token_id = token_feats['id']
                disconnected_tokens_digraph.add_node(token_id, **token_feats)

        document_level_modal_dependencies_graph = self.modal_dependency_parse_to_networkx(serif_doc)
        sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(s) for s in serif_doc.sentences]
        sentence_level_amr_graphs = [self.amr_parse_to_networkx(s) for s in serif_doc.sentences]

        # compose into one document-level networkx DiGraph
        G = nx.algorithms.operators.compose_all(
                [disconnected_tokens_digraph] + \
                [document_level_modal_dependencies_graph] + \
                sentence_level_dependency_syntax_graphs + \
                sentence_level_amr_graphs
            )

        if not nx.algorithms.dag.is_directed_acyclic_graph(G):
            logging.warning("Cycle detected in graph for %s" % serif_doc.id)
            logging.warning(str(nx.algorithms.cycles.find_cycle(G)))
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

        for parent_mtrm in mtrm_list:

            # create parent node
            parent_mtrm_feats = self.modal_temporal_relation_mention_to_feats(parent_mtrm)
            parent_mtrm_id = parent_mtrm_feats['id']
            G.add_node(parent_mtrm_id, **{k:v for k,v in parent_mtrm_feats.items() if type(v)==str})

            # connect parent node to all of its tokens
            parent_token_ids = [self.token_to_feats(t)['id'] for t in parent_mtrm_feats['tokens']]
            G.add_edges_from(list(map(lambda t: (parent_mtrm_id, t), parent_token_ids)),
                             **{EdgeAttrs.label: EdgeTypes.modal_constituent_token,
                                EdgeAttrs.edge_type: EdgeTypes.modal_constituent_token})

            for child_mtrm in parent_mtrm.children:

                # create child node
                child_mtrm_feats = self.modal_temporal_relation_mention_to_feats(child_mtrm)
                child_mtrm_id = child_mtrm_feats['id']
                G.add_node(child_mtrm_id, **{k:v for k,v in child_mtrm_feats.items() if type(v)==str})

                # connect child node to all of its tokens
                child_token_ids = [self.token_to_feats(t)['id'] for t in child_mtrm_feats['tokens']]
                G.add_edges_from(list(map(lambda t: (child_mtrm_id, t), child_token_ids)),
                                 **{EdgeAttrs.label: EdgeTypes.modal_constituent_token,
                                    EdgeAttrs.edge_type: EdgeTypes.modal_constituent_token})

                # modal dependency edge between parent and child nodes
                G.add_edge(parent_mtrm_id, child_mtrm_id,
                           **{EdgeAttrs.label: child_mtrm_feats[ModalNodeAttrs.modal_relation],
                              ModalEdgeAttrs.modal_relation: child_mtrm_feats[ModalNodeAttrs.modal_relation],
                              EdgeAttrs.edge_type: EdgeTypes.modal})

        try:
            assert nx.algorithms.dag.is_directed_acyclic_graph(G)
        except AssertionError:
            logging.warning("Cycle detected in MDP for %s" % serif_doc.id)
            logging.warning(str(nx.algorithms.cycles.find_cycle(G)))

        return G

    def syntactic_dependency_parse_to_networkx(self, serif_sentence):
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

    def amr_parse_to_networkx(self, serif_sentence):
        '''
        :param serif_sentence: serif.theory.sentence.Sentence
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        amr_parse = serif_sentence.amr_parse
        if amr_parse is None:
            return G

        root_amr_node = amr_parse.root
        root_amr_node_feats = self.amr_node_to_feats(root_amr_node)
        root_amr_node_id = root_amr_node_feats['id']

        # perform BFS starting from root amr node

        visited = []  # List to keep track of visited nodes.
        queue = []  # Initialize a queue

        visited.append(root_amr_node_id)
        queue.append(root_amr_node)

        while queue:

            curr_amr_node = queue.pop(0)

            curr_amr_node_feats = self.amr_node_to_feats(curr_amr_node)
            curr_amr_node_id = curr_amr_node_feats['id']
            G.add_node(curr_amr_node_id, **{k: v for k, v in curr_amr_node_feats.items() if type(v) == str})

            # add edges to aligned tokens (if there are any)
            if curr_amr_node.tokens is not None:

                for aligned_token in curr_amr_node.tokens:

                    aligned_token_feats = self.token_to_feats(aligned_token)
                    aligned_token_id = aligned_token_feats['id']

                    G.add_edge(curr_amr_node_id, aligned_token_id,
                               **{EdgeAttrs.label: EdgeTypes.amr_aligned_token,
                                  EdgeAttrs.edge_type: EdgeTypes.amr_aligned_token})

            # iterate over child nodes
            for i, child_amr_node in enumerate(curr_amr_node._children):

                child_amr_node_feats = self.amr_node_to_feats(child_amr_node)
                child_amr_node_id = child_amr_node_feats['id']

                if child_amr_node_id not in visited:

                    G.add_node(child_amr_node_id, **{k: v for k, v in child_amr_node_feats.items() if type(v) == str})

                    G.add_edge(curr_amr_node_id, child_amr_node_id,
                               **{EdgeAttrs.label: json.loads(curr_amr_node._outgoing_amr_rels)[i],
                                  AMREdgeAttrs.amr_relation: json.loads(curr_amr_node._outgoing_amr_rels)[i],
                                  EdgeAttrs.edge_type: EdgeTypes.amr})

                    visited.append(child_amr_node_id)
                    queue.append(child_amr_node)

        return G

    def token_to_feats(self, token):
        '''
        :type token: serif.theory.token.Token
        :return: dict
        '''

        feats = {NodeAttrs.id: ID_DELIMITER.join([token.text, token.id]),
                 NodeAttrs.node_type: NodeTypes.token,
                 TokenNodeAttrs.text: token.text,
                 TokenNodeAttrs.upos: token.upos,
                 TokenNodeAttrs.xpos: token.xpos,
                 TokenNodeAttrs.index_in_doc: "_".join([str(token.sentence.sent_no), str(token.index()), str(token.index())]),
                 TokenNodeAttrs.incoming_dep_rel: token.dep_rel}

        return feats

    def modal_temporal_relation_mention_to_feats(self, mtrm):
        '''
        :param mtrm: serif.theory.modal_temporal_relation_mention.ModalTemporalRelationMention
        :return: dict
        '''

        mtra = mtrm.node  # modal_temporal_relation_argument

        special_name = "Null"  # default "Null" value for regular mtra nodes (node_match functions will match if only one of the values is None)
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

            NodeAttrs.id: ID_DELIMITER.join([mtra.id]),  # TODO or mtrm.id + mtra.id ?
            NodeAttrs.node_type: NodeTypes.modal,

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

    def amr_node_to_feats(self, amr_node):
        '''
        :param amr_node: serif.theory.amr_node.AMRNode
        :return: dict
        '''

        feats = {

            NodeAttrs.id: ID_DELIMITER.join([amr_node.id, amr_node.varname, amr_node.content]),
            NodeAttrs.node_type: NodeTypes.amr,

            AMRNodeAttrs.varname: amr_node.varname,
            AMRNodeAttrs.content: amr_node.content

        }

        return feats

    def visualize_networkx_graph(self, G):
        from graph_viewer import GraphViewer
        GV = GraphViewer()
        GV.visualize_networkx_graph(G)
