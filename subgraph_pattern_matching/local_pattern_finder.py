from enum import Enum
import networkx as nx
from tqdm import tqdm
import argparse
import re
from annotation.annotation_base import FrameAnnotationTypes
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.types.edge_types import EdgeTypes
from io_utils.io_utils import serialize_patterns, serialize_pattern_graphs
from patterns.pattern import Pattern

class ParseTypes(Enum):
    '''which parses to look at'''

    DP  = 1  # syntactic dependency parse
    MDP = 2  # modal dependency parse
    TDP = 3  # temporal dependency parse
    AMR = 4  # abstract meaning representation parse


class DAGSearchDirection(Enum):
    '''whether to look only at parents (UP), only at children (DOWN), or at both (BOTH)'''

    UP = 1
    DOWN = 2
    BOTH = 3


PARSE_TYPE_TO_EDGE_TYPES = {
    ParseTypes.DP: {EdgeTypes.syntax},
    ParseTypes.MDP: {EdgeTypes.modal, EdgeTypes.modal_constituent_token},
    ParseTypes.TDP: {EdgeTypes.temporal, EdgeTypes.temporal_constituent_token},
    ParseTypes.AMR: {EdgeTypes.amr, EdgeTypes.amr_aligned_token}
}


PARSE_TYPE_COMBINATIONS = [
    [ParseTypes.DP],
    [ParseTypes.MDP],
    [ParseTypes.TDP],
    [ParseTypes.AMR],
    [ParseTypes.DP, ParseTypes.MDP],
    [ParseTypes.DP, ParseTypes.TDP],
    [ParseTypes.DP, ParseTypes.AMR],
    [ParseTypes.DP, ParseTypes.MDP, ParseTypes.TDP, ParseTypes.AMR]
]

def get_parse_type_kwargs(str_encoding):
    k, search_direction, parse_type_str = re.split('\.|_', str_encoding)
    parse_types = [ParseTypes(int(p)) for p in parse_type_str.split("-")]
    parse_types_kwargs = {parse_type.name.lower(): (parse_type in parse_types) for parse_type in ParseTypes}

    return parse_types_kwargs


class LocalPatternFinder():

    def __init__(self):
        pass


    def return_k_hop_neighborhood_of_node(self, G, node_id, k=1, parse_types=[ParseTypes.DP], search_direction=DAGSearchDirection.BOTH):
        '''


        :param G: networkx.classes.digraph.DiGraph
        :param node_id: str, source node id in G
        :param k: int, size of neighborhood
        :param parse_type: list[ParseTypes.X]
        :param search_direction: DAGSearchDirection.X

        :return: DiGraph for k-hop neighborhood of source node with edges for only specified parse types
        '''

        # nx.single_source_shortest_path returns dictionary from target node id to list of node ids corresponding to the
        #  shortest path from source to target; we only need to know which nodes are in the k-hop neighborhood of source
        #  node so we'll take the keys of that dictionary.


        if search_direction == DAGSearchDirection.BOTH:
            down_nodes = set(nx.single_source_shortest_path(G, node_id, cutoff=k).keys())
            up_nodes = set(nx.single_source_shortest_path(G.reverse(copy=True), node_id, cutoff=k).keys())
            neighborhood_nodes = down_nodes.union(up_nodes)

        elif search_direction == DAGSearchDirection.DOWN:
            neighborhood_nodes = set(nx.single_source_shortest_path(G, node_id, cutoff=k).keys())

        else: # search_direction == DAGSearchDirection.UP:
            neighborhood_nodes = set(nx.single_source_shortest_path(G.reverse(copy=True), node_id, cutoff=k).keys())

        # get subgraph induced by nodes in k-hop neighborhood of source node
        neighborhood_subgraph = G.subgraph(neighborhood_nodes)

        # # prune neighborhood subgraph by specified parse types (remove all other edges)
        # pruned_neighborhood_subgraph = self.get_edge_induced_subgraph_for_parse_types(neighborhood_subgraph,
        #                                                                               parse_types=parse_types)

        # return pruned_neighborhood_subgraph
        return neighborhood_subgraph


    def get_edge_induced_subgraph_for_parse_types(self, G, parse_types=[ParseTypes.DP]):
        '''

        :param G:
        :param parse_types:
        :return:
        '''

        # determine edge types allowed for specified parse types
        allowed_edge_types = set().union(*[PARSE_TYPE_TO_EDGE_TYPES[pt] for pt in parse_types])

        # retrieve allowed graph edges
        edges_for_parse_types = [e for e in G.edges if G.edges[e][EdgeAttrs.edge_type] in allowed_edge_types]

        # get edge induced subgraph for allowed edges
        edge_induced_subgraph = G.edge_subgraph(edges_for_parse_types)

        return edge_induced_subgraph


    def get_annotation_subgraphs(self, annotations, k, parse_types, search_direction, annotation_category=None, all_attrs=False,
                                 return_graphs_only=False):

        annotation_patterns_for_configuration = []

        print("# annotations: {}".format(len(annotations)))

        # loop over annotations
        for i, ann in enumerate(tqdm(annotations, desc="annotations", position=3, leave=False)):

            if annotation_category != None and annotation_category != "all_categories":
                if ann.category != annotation_category:
                    continue

            # if annotation consists of multiple tokens, compose their k-hop subgraphs
            token_k_hop_neighborhoods = []
            for token_node_id in ann.token_node_ids:
                token_k_hop_neighborhoods.append(
                    self.return_k_hop_neighborhood_of_node(G=ann.networkx_graph,
                                                           node_id=token_node_id,
                                                           k=k,
                                                           parse_types=parse_types,
                                                           search_direction=search_direction))

            ann_k_hop_neighborhood = nx.algorithms.operators.compose_all(token_k_hop_neighborhoods)
            ann_k_hop_neighborhood = ann.networkx_graph.subgraph(ann_k_hop_neighborhood.nodes())  # get node-induced subgraph, assume it will have no edges of unwanted parse types
            if len(ann_k_hop_neighborhood) == 0:
                continue

            neighborhood_copy = ann_k_hop_neighborhood.copy()
            for token_node_id in ann.token_node_ids:
                neighborhood_copy.nodes[token_node_id][NodeAttrs.annotated] = True
                for node_attr, label in ann.token_node_ids_to_node_attr_label[token_node_id]:
                    neighborhood_copy.nodes[token_node_id][node_attr] = label

            if return_graphs_only:

                annotation_patterns_for_configuration.append(neighborhood_copy)

            else:

                parse_type_string = "-".join([str(p.value) for p in parse_types])

                all_node_attrs = set()
                all_edge_attrs = set()
                if all_attrs:
                    for __, attr_dict in list(neighborhood_copy.nodes(data=True)):
                        for attr, __ in attr_dict.items():
                            if attr is NodeAttrs.annotated:
                                continue
                            all_node_attrs.add(attr)
                    for __, __, attr_dict in list(neighborhood_copy.edges(data=True)):
                        for attr, __ in attr_dict.items():
                            all_edge_attrs.add(attr)
                else:
                    all_node_attrs.add(NodeAttrs.node_type)
                    all_edge_attrs.add(EdgeAttrs.edge_type)

                grid_search_config = "{}_{}_{}".format(k, search_direction.value, parse_type_string)
                annotation_pattern = Pattern("id_{}_{}".format(i, grid_search_config), neighborhood_copy,
                                             list(all_node_attrs), list(all_edge_attrs),
                                             grid_search=grid_search_config,
                                             category=annotation_category)
                annotation_patterns_for_configuration.append(annotation_pattern)

        return annotation_patterns_for_configuration


    def grid_search(self,
                    annotations,
                    k_values=[1,2,3,4,5],
                    parse_type_combinations=PARSE_TYPE_COMBINATIONS,
                    search_directions=[DAGSearchDirection.DOWN, DAGSearchDirection.UP, DAGSearchDirection.BOTH]):
        '''

        :param annotations: list[annotation.annotation.Annotation]
        :param k_values: list[int]
        :param parse_type_combinations: list[list[ParseTypes.X]]
        :param search_directions: list[DAGSearchDirections.X]

        :return: {tup: list[networkx.classes.digraph.DiGraph]}
        '''

        config_to_annotation_subgraphs = dict()

        # loop over k-hop neighborhood configurations
        for k in tqdm(k_values, desc='k-hop neighborhoods', position=0):
            for parse_types in tqdm(parse_type_combinations, desc='parse type combinations', position=1, leave=False):
                for search_direction in tqdm(search_directions, desc='search combinations', position=2, leave=False):

                    config = (k, tuple(parse_types), search_direction)
                    annotation_subgraphs_for_configuration = self.get_annotation_subgraphs(annotations, k, parse_types, search_direction)

                    config_to_annotation_subgraphs[config] = annotation_subgraphs_for_configuration

        return config_to_annotation_subgraphs


def read_corpus(corpus_id, parse_types=None):
    '''

    :param corpus_id: str
    :param parse_types: None or {'dp': True, 'mdp': False, 'tdp': False, 'amr': True}
    :return:
    '''

    from annotation.ingestion.event_ingester import EventIngester
    from annotation.ingestion.ner_ingester import NERIngester
    from annotation.ingestion.relation_ingester import RelationIngester

    if corpus_id == "TACRED":
        corpus = RelationIngester(parse_types).ingest_tacred()
    elif corpus_id == "CONLL_ENGLISH":
        corpus = NERIngester(parse_types).ingest_conll()
    elif corpus_id == "ACE_ENGLISH":
        corpus = EventIngester(parse_types).ingest_ace()
    elif corpus_id == "AIDA_TEST":
        corpus = EventIngester(parse_types).ingest_aida()
    else:
        raise NotImplementedError("Corpus {} not implemented".format(corpus_id))

    return corpus


def main(args):

    parse_types = [ParseTypes[p] for p in args.parse_types]
    parse_types_kwargs = {parse_type.name.lower(): (parse_type in parse_types) for parse_type in ParseTypes}

    corpus = read_corpus(args.annotation_corpus, parse_types=parse_types_kwargs)

    LPF = LocalPatternFinder()

    annotation_patterns = LPF.get_annotation_subgraphs(annotations=corpus.train_annotations,
                                                       k=args.k_hop_neighborhoods,
                                                       parse_types=parse_types,
                                                       search_direction=DAGSearchDirection[args.search_direction],
                                                       annotation_category=args.annotation_category,
                                                       all_attrs=args.all_attrs,
                                                       return_graphs_only=args.create_dataset_for_spminer)

    if args.create_graphs_for_spminer:

        json_dump = serialize_pattern_graphs(annotation_patterns)
        with open(args.output, 'w') as f:
            f.write(json_dump)

    else:

        json_dump = serialize_patterns(annotation_patterns)
        with open(args.output, 'w') as f:
            f.write(json_dump)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annotation_corpus', type=str, required=True)
    parser.add_argument('-o', '--output', type=str, required=True)
    parser.add_argument('-k', '--k_hop_neighborhoods', type=int, default=1)
    parser.add_argument('-p', '--parse_types', nargs="*", type=str, default=PARSE_TYPE_COMBINATIONS)
    parser.add_argument('-s', '--search_direction', type=str, default=DAGSearchDirection.BOTH)
    parser.add_argument('-c', '--annotation_category', type=str, default="all_categories")
    parser.add_argument('--all_attrs', action='store_true')
    parser.add_argument('--create_graphs_for_spminer', action='store_true')
    args = parser.parse_args()
    main(args)
