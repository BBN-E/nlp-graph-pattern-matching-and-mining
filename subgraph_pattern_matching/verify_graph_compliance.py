
from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs, \
    PatternTokenNodes, PatternModalNodes, PatternEdges, \
    PatternTokenNodeIDs, PatternModalNodeIDs


def verify_graph_compliance(G):
    '''ensure graph has desired attributes'''

    for (id, attrs) in G.nodes(data=True):
        assert NodeAttrs.node_type in attrs

