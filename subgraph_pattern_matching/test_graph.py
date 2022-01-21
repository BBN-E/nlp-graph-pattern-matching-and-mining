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
#####################        Create Document Graph        #####################
###############################################################################
G = nx.DiGraph()

G.add_node('said', nodeType=NodeTypes.token, upos='VERB')
G.add_node('Cross', nodeType=NodeTypes.token, upos='PROPN')
G.add_node('believed', nodeType=NodeTypes.token, upos='VERB')
G.add_node('missing', nodeType=NodeTypes.token, upos='VERB')
G.add_node('landslide', nodeType=NodeTypes.token, upos='NOUN')
G.add_node('buried', nodeType=NodeTypes.token, upos='VERB')

G.add_edge('said', 'Cross', edgeType=EdgeTypes.syntax, depRel='nsubj')
G.add_edge('said', 'believed', edgeType=EdgeTypes.syntax, depRel='ccomp')
G.add_edge('believed', 'missing', edgeType=EdgeTypes.syntax, depRel='conj')
G.add_edge('missing', 'buried', edgeType=EdgeTypes.syntax, depRel='advcl')
G.add_edge('buried', 'landslide', edgeType=EdgeTypes.syntax, depRel='nsubj')

G.add_node('CONCEIVER<the Red Cross>', nodeType=NodeTypes.modal, modalNodeType='Conceiver')
G.add_node('EVENT<missing>', nodeType=NodeTypes.modal, modalNodeType='Event')
G.add_node('EVENT<landslide>', nodeType=NodeTypes.modal, modalNodeType='Event')

G.add_edge('CONCEIVER<the Red Cross>', 'Cross', edgeType=EdgeTypes.constituent_token)
G.add_edge('EVENT<missing>', 'missing', edgeType=EdgeTypes.constituent_token)
G.add_edge('EVENT<landslide>', 'landslide', edgeType=EdgeTypes.constituent_token)

# # TODO activating these will make the matching not work -- adding edges this way must eliminate node info
# G.add_edge('CONCEIVER<the Red Cross>', 'EVENT<missing>', edgeType=EdgeTypes.modal)
# G.add_edge('CONCEIVER<the Red Cross>', 'EVENT<landslide>', edgeType=EdgeTypes.modal)

###############################################################################



###############################################################################
#####################      NetworkX Pattern Matching      #####################
###############################################################################
pattern = nx.DiGraph()

pattern.add_nodes_from([
    # PatternTokenNodes.CONCEIVER_TOKEN_NODE,
    # PatternTokenNodes.SIP_TOKEN_NODE,
    # PatternTokenNodes.EVENT_TOKEN_NODE,
    PatternModalNodes.CONCEIVER_NODE,
    PatternModalNodes.EVENT_NODE,
])

# pattern.add_edges_from([

    # # SIP -(nsubj)-> ConceiverToken
    # (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
    #  {EdgeAttrs.edgeType: EdgeTypes.syntax, SyntaxEdgeAttrs.depRel: 'nsubj'}),
    #
    # # SIP -(ccomp)-> EventToken
    # (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID, PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
    #  {EdgeAttrs.edgeType: EdgeTypes.syntax, SyntaxEdgeAttrs.depRel: 'ccomp'}),

    # PatternEdges.CONCEIVER_EVENT_EDGE,
    # PatternEdges.CONCEIVER_TOKEN_EDGE,
    # PatternEdges.EVENT_TOKEN_EDGE

# ])

Factory = PatternFactory()
_, node_match, edge_match = Factory.relaxed_ccomp_pattern()

matcher = nx.algorithms.isomorphism.DiGraphMatcher(G, pattern,
                                                   node_match=node_modal_type_match,
                                                   edge_match=edge_match)
matches = [g for g in matcher.subgraph_isomorphisms_iter()]
print(matches)


###############################################################################
#####################      DotMotif Pattern Matching      #####################
###############################################################################

from dotmotif import Motif, NetworkXExecutor, GrandIsoExecutor

G1 = nx.DiGraph()
G1.add_node('A', name='Wilbur')
# import pdb; pdb.set_trace()
G1.add_node('B')
G1.add_node('C', name='Wallace')
G1.add_node('D')
G1.add_edge('A', 'B')
G1.add_edge('C', 'D')
G1.add_edge('A', 'C')

# import pdb; pdb.set_trace()

motif = Motif('''
    A -> B
    C -> D
    A.name = "Wilbur"
    C.name = "Wallace"
    ''')

E = NetworkXExecutor(graph=G1)
matches = E.find(motif)
print(matches)