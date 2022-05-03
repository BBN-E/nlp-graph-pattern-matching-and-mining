import networkx as nx
from match_utils.node_match_functions import node_multiple_attrs_match, node_attr_match, node_type_match
from match_utils.edge_match_functions import edge_multiple_attrs_match, edge_attr_match, edge_type_match
from networkx.readwrite import json_graph
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.node.node_attrs import NodeAttrs



class Pattern():

    def __init__(self, pattern_id=None, pattern_graph=None, node_attrs=None, edge_attrs=None, grid_search=None, category=None):

        self._pattern_id = pattern_id
        self._pattern_graph = pattern_graph
        self._node_attrs = node_attrs
        self._edge_attrs = edge_attrs
        self._node_match = None
        self._edge_match = None
        if node_attrs:
            self.make_node_match()
        if edge_attrs:
            self.make_edge_match()
        self.grid_search = grid_search
        self.category = category

    @property
    def pattern_id(self):
        return self._pattern_id

    @property
    def pattern_graph(self):
        return self._pattern_graph

    def make_node_match(self):
        match_funcs = []

        # https://stackoverflow.com/questions/54288926/python-loops-and-closures
        for attr in self._node_attrs:

            if attr == NodeAttrs.node_type:
                def node_match_closure(n1, n2):
                    return node_type_match(n1, n2)
            else:
                def node_match_closure(n1, n2, attr_val=attr):
                    return node_attr_match(n1, n2, attr_val)

            match_funcs.append(node_match_closure)
        self._node_match = node_multiple_attrs_match(*match_funcs)


    def make_edge_match(self):
        match_funcs = []
        for attr in self._edge_attrs:

            if attr == EdgeAttrs.edge_type:
                def edge_match_closure(n1, n2):
                    return edge_type_match(n1, n2)
            else:
                def edge_match_closure(e1, e2, attr_val=attr):
                    return edge_attr_match(e1, e2, attr_val)

            match_funcs.append(edge_match_closure)
        self._edge_match = edge_multiple_attrs_match(*match_funcs)

    @property
    def node_match(self):
        return self._node_match

    @property
    def edge_match(self):
        return self._edge_match

    def to_json(self):
        jgraph = json_graph.node_link_data(self._pattern_graph)

        json_dict = {'pattern_id': self._pattern_id,
                     'pattern_graph': jgraph,
                     'node_attrs': self._node_attrs,
                     'edge_attrs': self._edge_attrs,
                     'grid_search': self.grid_search,
                     'category': self.category}
        return json_dict

    def load_from_json(self, json_dict):
        self._pattern_id = json_dict['pattern_id']
        self._pattern_graph = json_graph.node_link_graph(json_dict['pattern_graph'])
        self._node_attrs = json_dict['node_attrs']
        self._edge_attrs = json_dict['edge_attrs']
        if json_dict['grid_search']:
            self.grid_search = json_dict['grid_search']
        if json_dict['category']:
            self.category = json_dict['category']
        if self._node_attrs:
            self.make_node_match()
        if self._edge_attrs:
            self.make_edge_match()

    def get_annotated_node_ids(self):
        annotated_node_ids = set()
        for node in self.pattern_graph:
            if NodeAttrs.annotated in self.pattern_graph.nodes[node]:
                annotated_node_ids.add(node)

        if len(annotated_node_ids) <= 0:
            return None

        return annotated_node_ids


