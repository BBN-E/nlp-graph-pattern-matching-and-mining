import networkx as nx
from dotmotif import Motif, NetworkXExecutor, GrandIsoExecutor

import logging

from timer import timer

logging.basicConfig(level=logging.INFO)

@timer
def build_networkx_digraph():
    G = nx.DiGraph()
    G.add_node('A', attr='top')
    G.add_node('B', attr='top')
    G.add_node('C', attr='bottom')
    G.add_node('D', attr='bottom')
    G.add_edge('A', 'C')
    G.add_edge('B', 'D')
    return G

############################################################################
@timer
def build_pattern_digraph():
    pattern = nx.DiGraph()
    pattern.add_node('T')
    pattern.add_node('B')
    pattern.add_edge('T', 'B')
    return pattern

@timer
def build_digraph_matcher(G, pattern):
    matcher = nx.algorithms.isomorphism.DiGraphMatcher(G, pattern,
                                                       node_match=None,
                                                       edge_match=None)
    return matcher

@timer
def subgraph_isomorphisms(matcher):
    matches = [g for g in matcher.subgraph_isomorphisms_iter()]
    return matches

def networkx_run(G):
    # step 1
    pattern = build_pattern_digraph()
    # step 2
    matcher = build_digraph_matcher(G, pattern)
    # step 3
    matches = subgraph_isomorphisms(matcher)
    return matches
############################################################################

############################################################################
@timer
def build_motif():
    motif = Motif('''
    T -> B
    ''')
    return motif

@timer
def build_executor(G):
    executor = NetworkXExecutor(graph=G)
    return executor

@timer
def dotmotif_match(executor, motif):
    matches = executor.find(motif)
    return matches

def dotmotif_run(G):
    # step 1
    motif = build_motif()
    # step 2
    executor = build_executor(G)
    # step 3
    matches = dotmotif_match(executor, motif)
    return matches
############################################################################

if __name__ == '__main__':

    G = build_networkx_digraph()
    
    print(networkx_run(G))
    print("\n\n")
    print(dotmotif_run(G))