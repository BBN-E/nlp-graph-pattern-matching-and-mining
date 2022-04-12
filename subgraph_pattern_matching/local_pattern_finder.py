from enum import Enum
import networkx as nx

from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.types.edge_types import EdgeTypes


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


class LocalPatternFinder():

    def __init__(self):
        pass

    def return_k_hop_neighborhood_of_node(self,
                                          G,
                                          node,
                                          k=1,
                                          parse_types=[ParseTypes.DP],
                                          search_direction=DAGSearchDirection.BOTH):
        '''

        :param G: networkx.classes.digraph.DiGraph
        :param node: str, source node id in G
        :param k: int, size of neighborhood
        :param parse_type: list[ParseTypes.X]
        :param search_direction: DAGSearchDirection.X

        :return: DiGraph for k-hop neighborhood of source node with edges for only specified parse types
        '''

        # nx.single_source_shortest_path returns dictionary from target node id to list of node ids corresponding to the
        #  shortest path from source to target; we only need to know which nodes are in the k-hop neighborhood of source
        #  node so we'll take the keys of that dictionary.

        if search_direction == DAGSearchDirection.BOTH:
            down_nodes = set(nx.single_source_shortest_path(G, node, cutoff=k).keys())
            up_nodes = set(nx.single_source_shortest_path(G.reverse(copy=True), node, cutoff=k).keys())
            neighborhood_nodes = down_nodes.union(up_nodes)

        elif search_direction == DAGSearchDirection.DOWN:
            neighborhood_nodes = set(nx.single_source_shortest_path(G, node, cutoff=k).keys())

        else: # search_direction == DAGSearchDirection.UP:
            neighborhood_nodes = set(nx.single_source_shortest_path(G.reverse(copy=True), node, cutoff=k).keys())

        # get subgraph induced by nodes in k-hop neighborhood of source node
        neighborhood_subgraph = G.subgraph(neighborhood_nodes)

        # prune neighborhood subgraph by specified parse types (remove all other edges)
        pruned_neighborhood_subgraph = self.get_edge_induced_subgraph_for_parse_types(neighborhood_subgraph,
                                                                                      parse_types=parse_types)

        return pruned_neighborhood_subgraph


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


if __name__ == '__main__':
    from graph_builder import GraphBuilder
    import serifxml3

    serif_doc = serifxml3.Document("/nfs/raid66/u11/users/brozonoy-ad/mtdp_runs/universal_parse/output.amr/universal_sentence.xml")

    GB = GraphBuilder()
    G = GB.serif_doc_to_networkx(serif_doc)

    LPF = LocalPatternFinder()
    # import pdb; pdb.set_trace()

    g = LPF.return_k_hop_neighborhood_of_node(G, 'smile__a12', k=5, parse_types=[ParseTypes.DP, ParseTypes.AMR], search_direction=DAGSearchDirection.BOTH)
    import pdb; pdb.set_trace()

    # LPF.return_kth_neighborhood_of_node(G, )
