
from io_utils.io_utils import serialize_patterns, deserialize_patterns

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


class PatternFactory():

    def __init__(self):

        self.patterns = [ccomp_pattern,
                         relaxed_ccomp_pattern,
                         relaxed_ccomp_one_hop_pattern,
                         according_to_pattern,
                         # author_conceiver_event_edge_pattern_0,
                         author_conceiver_event_edge_pattern_1,
                         author_conceiver_event_edge_pattern_2,
                         author_conceiver_event_edge_pattern_3,
                         as_reported_by_pattern]

        self.basic_patterns = [grounded_conceiver_event_edge_pattern]

        # self.amr_patterns = self.create_propbank_frames_patterns()
        self.amr_patterns = [person_says_x_pattern]

        self.loaded_patterns = {}

    def load_patterns(self, json_dump, is_file_path=False):

        self.loaded_patterns = deserialize_patterns(json_dump, is_file_path)

        return self.loaded_patterns

    def serialize_factory_patterns(self):
        return serialize_patterns(self.patterns)


if __name__ == '__main__':
    Factory = PatternFactory()
    pattern_graphs = Factory.serialize_factory_patterns()
    deserialized = deserialize_patterns(pattern_graphs)
    from view_utils.graph_viewer import GraphViewer

    graph_viewer = GraphViewer()

    for index, pattern in enumerate(deserialized):
        graph_viewer.prepare_mdp_networkx_for_visualization(pattern.pattern_graph)
        graph_viewer.prepare_networkx_for_visualization(pattern.pattern_graph)
        graph_viewer.visualize_networkx_graph(pattern.pattern_graph, html_file="serialization_sample_{}.html".format(index))


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
