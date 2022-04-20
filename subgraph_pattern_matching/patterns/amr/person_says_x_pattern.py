import networkx as nx

from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.amr_edge_attrs import AMREdgeAttrs
from constants.common.types.node_types import NodeTypes
from constants.common.types.edge_types import EdgeTypes

from patterns.pattern import Pattern

def person_says_x_pattern():
    '''
    1) "John says that Mary is sad."
    2) "Mary is sad, according to John."

    Both (1) and (2) receive identical AMR parses with "say-01" at the root, and an :arg0 of type "person"
    '''

    pattern_graph = nx.DiGraph()

    pattern_graph.add_node("say-01", **{NodeAttrs.node_type: NodeTypes.amr,
                            AMRNodeAttrs.content: "say-01"})
    pattern_graph.add_node("person", **{NodeAttrs.node_type: NodeTypes.amr,
                            AMRNodeAttrs.content: "person"})

    pattern_graph.add_edge("say-01", "person", **{EdgeAttrs.edge_type: EdgeTypes.amr,
                                      AMREdgeAttrs.amr_relation: ":arg0"})

    node_attrs = [AMRNodeAttrs.content]
    edge_attrs = [AMREdgeAttrs.amr_relation]

    return Pattern('person_says_x_pattern', pattern_graph, node_attrs, edge_attrs)