import re
import networkx as nx

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs, \
    PatternTokenNodes, PatternModalNodes, PatternEdges, \
    PatternTokenNodeIDs, PatternModalNodeIDs

from pattern_factory import PatternFactory
from match_utils.node_match_functions import *
from match_utils.edge_match_functions import *

###############################################################################
G = nx.DiGraph()

G.add_node('said', node_type=NodeTypes.token, upos='VERB')
G.add_node('Cross', node_type=NodeTypes.token, upos='PROPN')
G.add_node('believed', node_type=NodeTypes.token, upos='VERB')
G.add_node('missing', node_type=NodeTypes.token, upos='VERB')
G.add_node('landslide', node_type=NodeTypes.token, upos='NOUN')
G.add_node('buried', node_type=NodeTypes.token, upos='VERB')

G.add_edge('said', 'Cross', edge_type=EdgeTypes.syntax, dep_rel='nsubj')
G.add_edge('said', 'believed', edge_type=EdgeTypes.syntax, dep_rel='ccomp')
G.add_edge('believed', 'missing', edge_type=EdgeTypes.syntax, dep_rel='conj')
G.add_edge('missing', 'buried', edge_type=EdgeTypes.syntax, dep_rel='advcl')
G.add_edge('buried', 'landslide', edge_type=EdgeTypes.syntax, dep_rel='nsubj')

G.add_node('CONCEIVER<the Red Cross>', node_type=NodeTypes.modal, modal_node_type='Conceiver')
G.add_node('EVENT<missing>', node_type=NodeTypes.modal, modal_node_type='Event')
G.add_node('EVENT<landslide>', node_type=NodeTypes.modal, modal_node_type='Event')

G.add_edge('CONCEIVER<the Red Cross>', 'Cross', edge_type=EdgeTypes.constituent_token)
G.add_edge('EVENT<missing>', 'missing', edge_type=EdgeTypes.constituent_token)
G.add_edge('EVENT<landslide>', 'landslide', edge_type=EdgeTypes.constituent_token)

import pdb; pdb.set_trace()

# TODO activating these will make the matching not work -- adding edges this way must eliminate node info
G.add_edge('CONCEIVER<the Red Cross>', 'EVENT<missing>', edge_type=EdgeTypes.modal)
G.add_edge('CONCEIVER<the Red Cross>', 'EVENT<landslide>', edge_type=EdgeTypes.modal)

import pdb; pdb.set_trace()

###############################################################################


pattern = nx.DiGraph()

pattern.add_nodes_from([
    # PatternTokenNodes.CONCEIVER_TOKEN_NODE,
    # PatternTokenNodes.SIP_TOKEN_NODE,
    # PatternTokenNodes.EVENT_TOKEN_NODE,
    PatternModalNodes.CONCEIVER_NODE,
    PatternModalNodes.EVENT_NODE,
])

pattern.add_edges_from([

    # # SIP -(nsubj)-> ConceiverToken
    # (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
    #  {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'nsubj'}),
    #
    # # SIP -(ccomp)-> EventToken
    # (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
    #  {EdgeAttrs.edge_type: EdgeTypes.syntax, SyntaxEdgeAttrs.dep_rel: 'ccomp'}),

    PatternEdges.CONCEIVER_EVENT_EDGE,
    # PatternEdges.CONCEIVER_TOKEN_EDGE,
    # PatternEdges.EVENT_TOKEN_EDGE

])

import pdb; pdb.set_trace()


Factory = PatternFactory()
_, node_match, edge_match = Factory.relaxed_ccomp_pattern()

matcher = nx.algorithms.isomorphism.DiGraphMatcher(G, pattern,
                                                   node_match=node_modal_type_match,
                                                   edge_match=edge_match)
matches = [g for g in matcher.subgraph_isomorphisms_iter()]
print(matches)