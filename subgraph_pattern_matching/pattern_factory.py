import json
from networkx.readwrite import json_graph

from patterns.dp_mdp.ccomp_pattern import ccomp_pattern
from patterns.dp_mdp.relaxed_ccomp_pattern import relaxed_ccomp_pattern
from patterns.dp_mdp.relaxed_ccomp_one_hop_pattern import relaxed_ccomp_one_hop_pattern
from patterns.dp_mdp.according_to_pattern import according_to_pattern
from patterns.dp_mdp.author_conceiver_event_edge_0_pattern import author_conceiver_event_edge_pattern_0
from patterns.dp_mdp.author_conceiver_event_edge_1_pattern import author_conceiver_event_edge_pattern_1
from patterns.dp_mdp.author_conceiver_event_edge_2_pattern import author_conceiver_event_edge_pattern_2
from patterns.dp_mdp.author_conceiver_event_edge_3_pattern import author_conceiver_event_edge_pattern_3
from patterns.dp_mdp.as_reported_by_pattern import as_reported_by_pattern
from patterns.dp_mdp.grounded_conceiver_event_edge_pattern import grounded_conceiver_event_edge_pattern

from patterns.amr.person_says_x_pattern import person_says_x_pattern


def serialize_pattern_graphs(pattern_graphs):
    """

    :param pattern_list: list[(networkx.classes.digraph.DiGraph]

    :return json formatted str
    """

    json_data = []
    for digraph in pattern_graphs:
        jgraph = json_graph.node_link_data(digraph)
        json_data.append(jgraph)

    json_dump = json.dumps(json_data)
    return json_dump


def deserialize_pattern_graphs(json_dump, is_file_path=False):

    if is_file_path:
        with open(json_dump, 'r') as f:
            json_data = json.load(f)
    else:
        json_data = json.loads(json_dump)

    pattern_graphs = []
    for jgraph in json_data:
        digraph = json_graph.node_link_graph(jgraph)
        pattern_graphs.append(digraph)

    return pattern_graphs


class PatternFactory():

    def __init__(self):

        self.patterns = {'ccomp': ccomp_pattern,
                         'relaxed_ccomp': relaxed_ccomp_pattern,
                         'relaxed_ccomp_one_hop': relaxed_ccomp_one_hop_pattern,
                         'according_to': according_to_pattern,
                         # 'author_conceiver_event_edge_0': self.author_conceiver_event_edge_pattern_0,
                         'author_conceiver_event_edge_1': author_conceiver_event_edge_pattern_1,
                         'author_conceiver_event_edge_2': author_conceiver_event_edge_pattern_2,
                         'author_conceiver_event_edge_3': author_conceiver_event_edge_pattern_3,
                         'as_reported_by': as_reported_by_pattern}

        self.basic_patterns = {'grounded_conceiver_event_edge': grounded_conceiver_event_edge_pattern}

        # self.amr_patterns = self.create_propbank_frames_patterns()
        self.amr_patterns = {'person_says_x_pattern': person_says_x_pattern}

        self.loaded_patterns = {}

    def load_patterns(self, json_dump, is_file_path=False, node_match=None, edge_match=None):

        pattern_graph_list = deserialize_pattern_graphs(json_dump, is_file_path)

        for i, graph in enumerate(pattern_graph_list):
            def pattern_function():
                return graph, node_match, edge_match

            self.loaded_patterns["pattern_" + str(i)] = pattern_function

        return self.loaded_patterns

    def serialize_factory_patterns(self):
        pattern_graph_list = []
        for pattern_id, pattern in self.patterns.items():
            pattern_graph, __, __ = pattern()
            pattern_graph_list.append(pattern_graph)

        return serialize_pattern_graphs(pattern_graph_list)


if __name__ == '__main__':
    Factory = PatternFactory()
    pattern_graphs = Factory.serialize_factory_patterns()
    deserialized = deserialize_pattern_graphs(pattern_graphs)
    from view_utils.graph_viewer import GraphViewer

    graph_viewer = GraphViewer()

    for index, graph in enumerate(deserialized):
        graph_viewer.prepare_mdp_networkx_for_visualization(graph)
        graph_viewer.prepare_networkx_for_visualization(graph)
        graph_viewer.visualize_networkx_graph(graph, html_file="serialization_sample_{}.html".format(index))


# def create_propbank_frames_patterns(self):
    #
    #     from utils.load_propbank_to_xpo_mapping import load_propbank_to_xpo_mapping
    #     propbank_to_xpo = load_propbank_to_xpo_mapping()
    #
    #     pb_frame_to_nx_pattern = dict()
    #     for pb_frame in propbank_to_xpo.keys():
    #         G = nx.DiGraph()
    #         G.add_node(pb_frame, **{NodeAttrs.node_type: NodeTypes.amr,
    #                                 AMRNodeAttrs.content: pb_frame})
    #         pb_frame_to_nx_pattern[pb_frame] = lambda: (G, node_amr_match, None)
    #
    #     return pb_frame_to_nx_pattern
