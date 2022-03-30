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
