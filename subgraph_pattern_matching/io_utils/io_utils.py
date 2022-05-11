import json
from networkx.readwrite import json_graph
from patterns.pattern import Pattern
import os

def combine_pattern_lists(json_dump_paths):
    all_pattern_list = []
    for json_dump_path in json_dump_paths:
        pattern_list = deserialize_patterns(json_dump_path, is_file_path=True)
        all_pattern_list.extend(pattern_list)

    print(len(all_pattern_list))

    json_dump = serialize_patterns(all_pattern_list)
    return json_dump


def serialize_patterns(pattern_list):
    json_data = []
    for pattern in pattern_list:
        json_dict = pattern.to_json()
        json_data.append(json_dict)

    json_dump = json.dumps(json_data, indent=4)
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

    json_dump = json.dumps(json_data, indent=4)
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


def split_by_config(file_path, output_dir):

    config_to_pattern_list = {}

    patterns = deserialize_patterns(file_path, is_file_path=True)
    for pattern in patterns:
        if pattern.grid_search not in config_to_pattern_list:
            config_to_pattern_list[pattern.grid_search] = []

        config_to_pattern_list[pattern.grid_search].append(pattern)

    for config, pattern_list in config_to_pattern_list.items():
        serialized_patterns = serialize_patterns(pattern_list)
        with open(os.path.join(output_dir, config + ".json"), 'w') as f:
            f.write(serialized_patterns)

