import networkx as nx

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.amr_edge_attrs import AMREdgeAttrs
from constants.common.types.node_types import NodeTypes
from constants.common.types.edge_types import EdgeTypes

from match_utils.node_match_functions import node_amr_match
from match_utils.edge_match_functions import edge_amr_relation_match


def person_says_x_pattern():
    '''
    1) "John says that Mary is sad."
    2) "Mary is sad, according to John."

    Both (1) and (2) receive identical AMR parses with "say-01" at the root, and an :arg0 of type "person"
    '''

    G = nx.DiGraph()

    G.add_node("say-01", **{NodeAttrs.node_type: NodeTypes.amr,
                            AMRNodeAttrs.content: "say-01"})
    G.add_node("person", **{NodeAttrs.node_type: NodeTypes.amr,
                            AMRNodeAttrs.content: "person"})

    G.add_edge("say-01", "person", **{EdgeAttrs.edge_type: EdgeTypes.amr,
                                      AMREdgeAttrs.amr_relation: ":arg0"})

    return G, node_amr_match, edge_amr_relation_match
