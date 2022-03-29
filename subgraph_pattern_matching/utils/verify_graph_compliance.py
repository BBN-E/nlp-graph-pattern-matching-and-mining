from constants.common.attrs.node.node_attrs import NodeAttrs

def verify_graph_compliance(G):
    '''ensure graph has desired attributes'''

    for (id, attrs) in G.nodes(data=True):
        assert NodeAttrs.node_type in attrs, attrs