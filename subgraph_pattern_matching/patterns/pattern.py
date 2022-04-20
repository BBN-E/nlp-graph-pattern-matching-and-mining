import networkx as nx
from match_utils.node_match_functions import node_multiple_attrs_match, node_attr_match
from match_utils.edge_match_functions import edge_multiple_attrs_match, edge_attr_match
from networkx.readwrite import json_graph

class Pattern():

    def __init__(self, pattern_id=None, pattern_graph=None, node_attrs=None, edge_attrs=None):

        self._pattern_id = pattern_id
        self._pattern_graph = pattern_graph
        self._node_attrs = node_attrs
        self._edge_attrs = edge_attrs

    @property
    def pattern_id(self):
        return self._pattern_id

    @property
    def pattern_graph(self):
        return self._pattern_graph

    @property
    def node_match(self):
        match_funcs = []
        for attr in self._node_attrs:

            def node_match_closure(n1, n2):
                return node_attr_match(n1, n2, attr)

            match_funcs.append(node_match_closure)

        return node_multiple_attrs_match(*match_funcs)

    @property
    def edge_match(self):
        match_funcs = []
        for attr in self._edge_attrs:

            def edge_match_closure(n1, n2):
                return edge_attr_match(n1, n2, attr)

            match_funcs.append(edge_match_closure)

        return edge_multiple_attrs_match(*match_funcs)


    def to_json(self):
        jgraph = json_graph.node_link_data(self._pattern_graph)

        json_dict = {'pattern_id': self._pattern_id,
                     'pattern_graph': jgraph,
                     'node_attrs': self._node_attrs,
                     'edge_attrs': self._edge_attrs}
        return json_dict

    def load_from_json(self, json_dict):
        self._pattern_id = json_dict['pattern_id']
        self._pattern_graph = json_graph.node_link_graph(json_dict['pattern_graph'])
        self._node_attrs = json_dict['node_attrs']
        self._edge_attrs = json_dict['edge_attrs']





