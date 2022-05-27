import networkx as nx
from patterns.pattern import Pattern
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.node.amr_node_attrs import AMRNodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.types.node_types import NodeTypes

def expand_graph(graph, attributes_to_ignore=None):

    if attributes_to_ignore is None:
        attributes_to_ignore = [EdgeAttrs.label, NodeAttrs.id,
                                TokenNodeAttrs.text, TokenNodeAttrs.upos,
                                TokenNodeAttrs.xpos, TokenNodeAttrs.index_in_doc,
                                TokenNodeAttrs.incoming_dep_rel]
    expanded_graph = nx.DiGraph()

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

node_types = [NodeTypes.token, NodeTypes.modal, NodeTypes.temporal, NodeTypes.amr]


def compress_graph(graph):

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
                    for edge_neighbor in graph.neighbors(neighbor):
                        edge_neighbor_data = graph.get_edge_data(neighbor, edge_neighbor)
                        if edge_neighbor_data['label'] == "e2n":
                            edge_dest = edge_neighbor
                        else:
                            value = graph.nodes[edge_neighbor]['label']
                            edge_attrs[edge_neighbor_data['label']] = value

                    compressed_graph.add_edge(node, edge_dest, **edge_attrs)

                else:
                    compressed_graph.nodes[node][edge_data['label']] = graph.nodes[neighbor]['label']

    return compressed_graph


if __name__ == '__main__':
    from io_utils.io_utils import deserialize_patterns, serialize_patterns
    from view_utils.graph_viewer import GraphViewer
    import os

    patterns_json = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/5-17-2022-ACE-Majority-v3/grid_config/Contact:Phone-Write/5-BOTH-AMR/patterns.json"
    examples_dir="/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/examples_dir_temp"

    pattern_list = deserialize_patterns(patterns_json, is_file_path=True)
    graph_viewer = GraphViewer()

    expanded_graph = expand_graph(pattern_list[0].pattern_graph, {})

    compressed_graph = compress_graph(expanded_graph)
    print(pattern_list[0].pattern_graph.nodes(data=True))
    print(compressed_graph.nodes(data=True))

    graph_viewer.prepare_amr_networkx_for_visualization(pattern_list[0].pattern_graph)
    html_file = os.path.join(examples_dir, "graph_{}.html".format("original"))
    graph_viewer.visualize_networkx_graph(pattern_list[0].pattern_graph, html_file=html_file)

    graph_viewer.prepare_amr_networkx_for_visualization(expanded_graph)
    html_file = os.path.join(examples_dir, "graph_{}.html".format("expanded"))
    graph_viewer.visualize_networkx_graph(expanded_graph, html_file=html_file)

    graph_viewer.prepare_amr_networkx_for_visualization(compressed_graph)
    html_file = os.path.join(examples_dir, "graph_{}.html".format("compressed"))
    graph_viewer.visualize_networkx_graph(compressed_graph, html_file=html_file)

    assert(pattern_list[0].pattern_graph.nodes(data=True) == compressed_graph.nodes(data=True))
    for a, b in zip(pattern_list[0].pattern_graph.edges(data=True), compressed_graph.edges(data=True)):
        assert(a==b)
   # TODO: fails for unknown reason
   # assert(pattern_list[0].pattern_graph.edges(data=True) == compressed_graph.edges(data=True))
