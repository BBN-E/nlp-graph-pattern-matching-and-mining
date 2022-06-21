import re
import json
import networkx as nx
import logging

from serif.theory.event_mention import EventMention
from serif.theory.mention import Mention
from serif.theory.value_mention import ValueMention

from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.amr_edge_attrs import AMREdgeAttrs
from constants.common.attrs.edge.modal_edge_attrs import ModalEdgeAttrs
from constants.common.attrs.edge.temporal_edge_attrs import TemporalEdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.attrs.node.temporal_node_attrs import TemporalNodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs

from constants.common.types.edge_types import EdgeTypes
from constants.common.types.node_types import NodeTypes

from utils.verify_graph_compliance import verify_graph_compliance

from constants.special_symbols import ID_DELIMITER


logging.basicConfig(level=logging.INFO)


class GraphBuilder():

    def __init__(self, dp=True, amr=True, mdp=False, tdp=False):
        '''specify which parse types we want to load into nx graph'''

        self.dp = dp
        self.amr = amr
        self.mdp = mdp
        self.tdp = tdp

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

        union_of_parse_graphs = [disconnected_tokens_digraph]
        if self.mdp:
            # document_level_modal_dependencies_graphs = [self.modal_dependency_parse_to_networkx(serif_doc)]
            union_of_parse_graphs.append(self.modal_dependency_parse_to_networkx(serif_doc))
        if self.tdp:
            # document_level_temporal_dependencies_graphs = [self.temporal_dependency_parse_to_networkx(serif_doc)]
            union_of_parse_graphs.append(self.temporal_dependency_parse_to_networkx(serif_doc))
        if self.dp:
            # sentence_level_dependency_syntax_graphs = [self.syntactic_dependency_parse_to_networkx(s) for s in serif_doc.sentences]
            union_of_parse_graphs.extend([self.syntactic_dependency_parse_to_networkx(s) for s in serif_doc.sentences])
        if self.amr:
            # sentence_level_amr_graphs = [self.amr_parse_to_networkx(s) for s in serif_doc.sentences]
            union_of_parse_graphs.extend([self.amr_parse_to_networkx(s) for s in serif_doc.sentences])

        # compose into one document-level networkx DiGraph
        G = nx.algorithms.operators.compose_all(union_of_parse_graphs)

        if not nx.algorithms.dag.is_directed_acyclic_graph(G):
            logging.warning("Cycle detected in graph for %s" % serif_doc.id)
            logging.warning(str(nx.algorithms.cycles.find_cycle(G)))
        verify_graph_compliance(G)

        return G

    def serif_doc_to_networkx_per_sentence(self, serif_doc):
        '''
        :param serif_doc: serif.theory.document.Document
        :return: list[networkx.classes.digraph.DiGraph]
        '''

        return [self.serif_sentence_to_networkx(s) for s in serif_doc.sentences]

    def serif_sentence_to_networkx(self, serif_sentence):
        '''
        :param serif_sentence: serif.theory.sentence.Sentence
        :return: networkx.classes.digraph.DiGraph
        '''

        # make sure all the tokens in the sentence exist beforehand
        disconnected_tokens_digraph = nx.DiGraph()
        for token in serif_sentence.token_sequence:
            token_feats = self.token_to_feats(token)
            token_id = token_feats['id']
            disconnected_tokens_digraph.add_node(token_id, **token_feats)

        union_of_parse_graphs = [disconnected_tokens_digraph]
        if self.dp:
            union_of_parse_graphs.append(self.syntactic_dependency_parse_to_networkx(serif_sentence))
        if self.amr:
            union_of_parse_graphs.append(self.amr_parse_to_networkx(serif_sentence))

        # compose into one sentence-level networkx DiGraph
        G = nx.algorithms.operators.compose_all(union_of_parse_graphs)

        if not nx.algorithms.dag.is_directed_acyclic_graph(G):
            logging.warning("Cycle detected in graph for %s" % serif_sentence.id)
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
            parent_mtrm_feats = self.modal_relation_mention_to_feats(parent_mtrm)
            parent_mtrm_id = parent_mtrm_feats['id']
            G.add_node(parent_mtrm_id, **{k:v for k,v in parent_mtrm_feats.items() if type(v)==str})

            # connect parent node to all of its tokens
            parent_token_ids = [self.token_to_feats(t)['id'] for t in parent_mtrm_feats['tokens']]
            G.add_edges_from(list(map(lambda t: (parent_mtrm_id, t), parent_token_ids)),
                             **{EdgeAttrs.label: EdgeTypes.modal_constituent_token,
                                EdgeAttrs.edge_type: EdgeTypes.modal_constituent_token})

            for child_mtrm in parent_mtrm.children:

                # create child node
                child_mtrm_feats = self.modal_relation_mention_to_feats(child_mtrm)
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

    def temporal_dependency_parse_to_networkx(self, serif_doc):

        '''
        :param serif_doc: serif.theory.document.Document
        :return: networkx.classes.digraph.DiGraph
        '''

        G = nx.DiGraph()

        if serif_doc.modal_temporal_relation_mention_set is None:
            return G

        mtrm_list = [m for m in serif_doc.modal_temporal_relation_mention_set if re.match("(.*)_time", m.node.model)]

        for parent_mtrm in mtrm_list:

            # create parent node
            parent_mtrm_feats = self.temporal_relation_mention_to_feats(parent_mtrm)
            parent_mtrm_id = parent_mtrm_feats['id']
            G.add_node(parent_mtrm_id, **{k:v for k,v in parent_mtrm_feats.items() if type(v)==str})

            # connect parent node to all of its tokens
            parent_token_ids = [self.token_to_feats(t)['id'] for t in parent_mtrm_feats['tokens']]
            G.add_edges_from(list(map(lambda t: (parent_mtrm_id, t), parent_token_ids)),
                             **{EdgeAttrs.label: EdgeTypes.temporal_constituent_token,
                                EdgeAttrs.edge_type: EdgeTypes.temporal_constituent_token})

            for child_mtrm in parent_mtrm.children:

                # create child node
                child_mtrm_feats = self.temporal_relation_mention_to_feats(child_mtrm)
                child_mtrm_id = child_mtrm_feats['id']
                G.add_node(child_mtrm_id, **{k:v for k,v in child_mtrm_feats.items() if type(v)==str})

                # connect child node to all of its tokens
                child_token_ids = [self.token_to_feats(t)['id'] for t in child_mtrm_feats['tokens']]
                G.add_edges_from(list(map(lambda t: (child_mtrm_id, t), child_token_ids)),
                                 **{EdgeAttrs.label: EdgeTypes.temporal_constituent_token,
                                    EdgeAttrs.edge_type: EdgeTypes.temporal_constituent_token})

                # temporal dependency edge between parent and child nodes
                G.add_edge(parent_mtrm_id, child_mtrm_id,
                           **{EdgeAttrs.label: child_mtrm_feats[TemporalNodeAttrs.temporal_relation],
                              TemporalEdgeAttrs.temporal_relation: child_mtrm_feats[TemporalNodeAttrs.temporal_relation],
                              EdgeAttrs.edge_type: EdgeTypes.temporal})

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
                assert token.dep_rel == 'root' or token.dep_rel is None
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

    def modal_relation_mention_to_feats(self, mtrm):
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

    def temporal_relation_mention_to_feats(self, mtrm):
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
            NodeAttrs.node_type: NodeTypes.temporal,

            TemporalNodeAttrs.special_name: special_name,
            TemporalNodeAttrs.mention: mention,
            TemporalNodeAttrs.event_mention: event_mention,
            TemporalNodeAttrs.value_mention: value_mention,

            TemporalNodeAttrs.sentence: sentence,
            TemporalNodeAttrs.tokens: tokens,

            TemporalNodeAttrs.temporal_node_type: mtra.modal_temporal_node_type,  # Event, Timex
            TemporalNodeAttrs.temporal_relation: mtra.relation_type  # before, after, overlap
        }

        return feats

    def amr_node_to_feats(self, amr_node):
        '''
        :param amr_node: serif.theory.amr_node.AMRNode
        :return: dict
        '''

        feats = {

            NodeAttrs.id: ID_DELIMITER.join([amr_node.varname, amr_node.content, amr_node.id]),
            NodeAttrs.node_type: NodeTypes.amr,

            AMRNodeAttrs.varname: amr_node.varname,
            AMRNodeAttrs.content: amr_node.content

        }

        return feats

    def gspan_graph_to_networkx(self, gspan_graph,
                                node_labels=None, edge_labels=None):
        G = nx.DiGraph()
        for vid in gspan_graph.vertices:
            if node_labels is not None:
                vlb = node_labels[int(gspan_graph.vertices[vid].vlb)]
            else:
                vlb = gspan_graph.vertices[vid].vlb
            G.add_node(vid, **{'label' : vlb})
        for vid1 in gspan_graph.vertices:
            if node_labels is not None:
                vlb1 = node_labels[int(gspan_graph.vertices[vid1].vlb)]
            else:
                vlb1 = gspan_graph.vertices[vid1].vlb
            edges = gspan_graph.vertices[vid1].edges
            for vid2 in edges:
                if edge_labels is not None:
                    elb = edge_labels[int(edges[vid2].elb)]
                else:
                    elb = edges[vid2].elb
                if node_labels is not None:
                    vlb2 = node_labels[(gspan_graph.vertices[vid2].vlb)]
                else:
                    vlb2 = gspan_graph.vertices[vid2].vlb
                G.add_edge(vid1, vid2, **{'label' : elb})
        return G

    @staticmethod
    def numerize_attribute_values(graphs):

        from collections import defaultdict

        NODE_ATTR_VAL_TO_NUM = defaultdict(lambda: defaultdict(int))
        EDGE_ATTR_VAL_TO_NUM = defaultdict(lambda: defaultdict(int))

        for g in graphs:
            nodes = list(g.nodes(data=True))
            edges = nx.to_edgelist(g)

            for (node_id, node_attrs) in nodes:
                for attr_name, attr_val in node_attrs.items():  # e.g. k="pos", v="NOUN"
                    if attr_val not in NODE_ATTR_VAL_TO_NUM[attr_name]:

                        id = len(NODE_ATTR_VAL_TO_NUM[attr_name].keys())

                        NODE_ATTR_VAL_TO_NUM[attr_name][attr_val] = id

            for (u_id, v_id, edge_attrs) in edges:
                for attr_name, attr_val in edge_attrs.items():  # e.g. k="deprel", v="nsubj"
                    if attr_val not in EDGE_ATTR_VAL_TO_NUM[attr_name]:

                        id = len(EDGE_ATTR_VAL_TO_NUM[attr_name].keys())

                        EDGE_ATTR_VAL_TO_NUM[attr_name][attr_val] = id

        EDGE_ATTR_NUM_TO_VAL = defaultdict(lambda: defaultdict(int))
        NODE_ATTR_NUM_TO_VAL = defaultdict(lambda: defaultdict(int))
        
        for attr_name in NODE_ATTR_VAL_TO_NUM:
            for k,v in NODE_ATTR_VAL_TO_NUM[attr_name].items():
                NODE_ATTR_NUM_TO_VAL[attr_name][v] = k

        for attr_name in EDGE_ATTR_VAL_TO_NUM:
            for k,v in EDGE_ATTR_VAL_TO_NUM[attr_name].items():
                EDGE_ATTR_NUM_TO_VAL[attr_name][v] = k

        return NODE_ATTR_VAL_TO_NUM, NODE_ATTR_NUM_TO_VAL, \
               EDGE_ATTR_VAL_TO_NUM, EDGE_ATTR_NUM_TO_VAL

    @staticmethod
    def numerize_graphs(graphs, node_v2n, edge_v2n):

        for g in graphs:

            for (node_id, node_attrs) in g.nodes(data=True):
                for attr_name, attr_value in node_attrs.items():
                    g.nodes[node_id][attr_name] = node_v2n[attr_name][attr_value]

            for (u_id, v_id, edge_attrs) in g.edges(data=True):
                for attr_name, attr_value in edge_attrs.items():
                    g.edges[(u_id, v_id)][attr_name] = edge_v2n[attr_name][attr_value]

        return graphs

    @staticmethod
    def denumerize_graphs(graphs, node_n2v, edge_n2v):

        for g in graphs:

            for (node_id, node_attrs) in g.nodes(data=True):
                for attr_name, attr_num in node_attrs.items():
                    g.nodes[node_id][attr_name] = node_n2v[attr_name][attr_num]

            for (u_id, v_id, edge_attrs) in g.edges(data=True):
                for attr_name, attr_num in edge_attrs.items():
                    g.edges[(u_id, v_id)][attr_name] = edge_n2v[attr_name][attr_num]

        return graphs

    @staticmethod
    def convert_directed_to_undirected(graphs):

        undirected_graphs = []
        for g in graphs:
            undirected_g = nx.Graph()
            undirected_g.add_nodes_from(g.nodes(data=True))
            for (u_id, v_id, edge_attrs) in g.edges(data=True):
                edge_node = "{}-{}-edge".format(u_id, v_id)
                new_edge_attrs = edge_attrs.copy()
                new_edge_attrs[NodeAttrs.node_type] = NodeTypes.edge
                undirected_g.add_node(edge_node, **new_edge_attrs)
                undirected_g.add_edge(u_id, edge_node, label="n2e")
                undirected_g.add_edge(edge_node, v_id, label="e2n")
            undirected_graphs.append(undirected_g)

        return undirected_graphs

    @staticmethod
    def convert_undirected_to_directed(graphs):

        directed_graphs = []
        for g in graphs:
            directed_g = nx.DiGraph()
            edge_nodes = []
            for node, attr_dict in g.nodes(data=True):
                if attr_dict[NodeAttrs.node_type] == NodeTypes.edge:
                    edge_nodes.append((node, attr_dict))
                else:
                    directed_g.add_node(node, **attr_dict)

            for edge_node, edge_node_attrs in edge_nodes:
                edges = g.edges(edge_node, data=True)
                if len(edges) < 2:
                    continue
                assert len(edges) == 2
                src = None
                dst = None
                for node1, node2, edge_attrs in edges:
                    if edge_attrs['label'] == 'n2e':
                        if node1 != edge_node:
                            src = node1
                        else:
                            src = node2
                    elif edge_attrs['label'] == 'e2n':
                        if node1 != edge_node:
                            dst = node1
                        else:
                            dst = node2

                assert src is not None and dst is not None

                del edge_node_attrs[NodeAttrs.node_type]
                directed_g.add_edge(src, dst, **edge_node_attrs)

            directed_graphs.append(directed_g)

        return directed_graphs

    @staticmethod
    def expand_graph(graph, attributes_to_ignore=None, digraph=True):

        if attributes_to_ignore is None:
            attributes_to_ignore = [EdgeAttrs.label, NodeAttrs.id,
                                    TokenNodeAttrs.text, TokenNodeAttrs.upos,
                                    TokenNodeAttrs.xpos, TokenNodeAttrs.index_in_doc,
                                    TokenNodeAttrs.incoming_dep_rel]
        if digraph:
            expanded_graph = nx.DiGraph()
        else:
            expanded_graph = nx.Graph()

        for node, attr_dict in graph.nodes(data=True):
            expanded_graph.add_node(node, label=attr_dict[NodeAttrs.node_type])
            for attr, value in attr_dict.items():
                if attr == NodeAttrs.node_type or attr in attributes_to_ignore:
                    continue
                attr_node = "{}-{}".format(node, attr)
                expanded_graph.add_node(attr_node, label=value)
                expanded_graph.add_edge(node, attr_node, label=attr)

        for node_a, node_b, attr_dict in graph.edges(data=True):
            edge_node = "{}-{}-edge".format(node_a, node_b)
            value = attr_dict[EdgeAttrs.edge_type] + "!_!edge"
            expanded_graph.add_node(edge_node, label=value)
            expanded_graph.add_edge(node_a, edge_node, label="n2e")
            expanded_graph.add_edge(edge_node, node_b, label="e2n")
            for attr, value in attr_dict.items():
                if attr == EdgeAttrs.edge_type or attr in attributes_to_ignore:
                    continue

                attr_node = "{}-{}".format(edge_node, attr)
                expanded_graph.add_node(attr_node, label=value)
                expanded_graph.add_edge(edge_node, attr_node, label=attr)

        return expanded_graph

    @staticmethod
    def compress_graph(graph):
        node_types = [NodeTypes.token, NodeTypes.modal, NodeTypes.temporal, NodeTypes.amr]

        compressed_graph = nx.DiGraph()

        for node, node_attrs in graph.nodes(data=True):
            if node_attrs['label'] in node_types:
                compressed_graph.add_node(node, **{NodeAttrs.node_type: node_attrs['label']})

                for neighbor in graph.neighbors(node):
                    edge_data = graph.get_edge_data(node, neighbor)
                    if edge_data['label'] == "n2e":
                        edge_type = graph.nodes[neighbor]['label']
                        edge_type = edge_type.replace("!_!edge", "")
                        edge_attrs = {EdgeAttrs.edge_type: edge_type}
                        edge_dest = None
                        for edge_neighbor in graph.neighbors(neighbor):
                            edge_neighbor_data = graph.get_edge_data(neighbor, edge_neighbor)
                            if edge_neighbor_data['label'] == "e2n":
                                edge_dest = edge_neighbor
                            elif edge_neighbor_data['label'] == "n2e":
                                continue
                            else:
                                value = graph.nodes[edge_neighbor]['label']
                                edge_attrs[edge_neighbor_data['label']] = value

                        if edge_dest:
                            compressed_graph.add_edge(node, edge_dest, **edge_attrs)
                    elif edge_data['label'] == "e2n":
                        continue
                    else:
                        compressed_graph.nodes[node][edge_data['label']] = graph.nodes[neighbor]['label']

        return compressed_graph


if __name__ == '__main__':
    import serifxml3
    d = serifxml3.Document("/nfs/raid83/u13/caml/users/mselvagg_ad/data/ACE_parsed/dev/AFP_ENG_20030305.0918.xml")
    GB = GraphBuilder()
    graphs = GB.serif_doc_to_networkx_per_sentence(d)

    undirected_graphs = GB.convert_directed_to_undirected(graphs)
    directed_graphs = GB.convert_undirected_to_directed(undirected_graphs)
    assert (graphs[0].nodes(data=True) == directed_graphs[0].nodes(data=True))
    for a, b in zip(graphs[0].edges(data=True), directed_graphs[0].edges(data=True)):
        assert(a==b)

    # n_v2n, n_n2v, e_v2n, e_n2v = GB.numerize_attribute_values(graphs)
    # graphs_prime = GB.denumerize_graphs(GB.numerize_graphs(graphs=graphs, node_v2n=n_v2n, edge_v2n=e_v2n), n_n2v, e_n2v)

    from utils.io_utils import deserialize_patterns
    from view_utils.graph_viewer import GraphViewer
    import os

    patterns_json = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/5-18-2022-expanded-gSpan-ACE-v2/grid_config/Contact:Phone-Write/6-BOTH-AMR/patterns.json"
    examples_dir="/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/examples_dir_temp"

    pattern_list = deserialize_patterns(patterns_json, is_file_path=True)
    graph_viewer = GraphViewer()

    expanded_graph = GraphBuilder.expand_graph(pattern_list[0].pattern_graph, {})

    compressed_graph = GraphBuilder.compress_graph(expanded_graph)
    # print(pattern_list[0].pattern_graph.nodes(data=True))
    # print(compressed_graph.nodes(data=True))

    graph_viewer.prepare_amr_networkx_for_visualization(pattern_list[0].pattern_graph)
    html_file = os.path.join(examples_dir, "graph_{}.html".format("original"))
    graph_viewer.visualize_networkx_graph(pattern_list[0].pattern_graph, html_file=html_file)
    #
    # graph_viewer.prepare_amr_networkx_for_visualization(expanded_graph)
    # html_file = os.path.join(examples_dir, "graph_{}.html".format("expanded"))
    # graph_viewer.visualize_networkx_graph(expanded_graph, html_file=html_file)

    graph_viewer.prepare_amr_networkx_for_visualization(compressed_graph)
    html_file = os.path.join(examples_dir, "graph_{}.html".format("compressed"))
    graph_viewer.visualize_networkx_graph(compressed_graph, html_file=html_file)

    assert pattern_list[0].pattern_graph.nodes(data=True) == compressed_graph.nodes(data=True)

    for node1, node2, attr_dict in pattern_list[0].pattern_graph.edges(data=True):
        assert pattern_list[0].pattern_graph.edges[node1, node2] == compressed_graph.edges[node1, node2]

    assert len(pattern_list[0].pattern_graph.edges(data=True)) == len(compressed_graph.edges(data=True))

   # assert(pattern_list[0].pattern_graph.edges(data=True) == compressed_graph.edges(data=True))

