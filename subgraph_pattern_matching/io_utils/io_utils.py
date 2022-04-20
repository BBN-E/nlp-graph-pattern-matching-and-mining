import json
from networkx.readwrite import json_graph
from patterns.pattern import Pattern

def serialize_patterns(pattern_list):
    json_data = []
    for pattern in pattern_list:
        json_dict = pattern.to_json()
        json_data.append(json_dict)

    json_dump = json.dumps(json_data)
    return json_dump


def deserialize_patterns(json_dump, is_file_path=False):
    if is_file_path:
        with open(json_dump, 'r') as f:
            json_data = json.load(f)
    else:
        json_data = json.loads(json_dump)

    pattern_list = []
    for pattern_dict in json_data:
        pattern = Pattern()
        pattern.load_from_json(pattern_dict)
        pattern_list.append(pattern)

    return pattern_list


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