import os, json
import argparse
import networkx as nx
from collections import defaultdict

import serifxml3

from graph_builder import GraphBuilder
from digraph_matcher_factory import DiGraphMatcherFactory
from match_wrapper import MatchWrapper, MatchCorpus

def graph_view(serif_doc, workspace):
    GB = GraphBuilder()
    # document_graph = GB.convert_serif_doc_to_networkx(serif_doc)
    # document_graph_html = os.path.join(workspace,"document_graph.html")
    # GB.visualize_networkx_graph(document_graph, document_graph_html)

    # MDPG = GB.modal_dependency_parse_to_networkx(serif_doc)
    # SDPG = [GB.syntactic_dependency_parse_to_networkx(s) for s in serif_doc.sentences]
    # mdpg_html = os.path.join(workspace,"mdpg_graph.html")
    # GB.visualize_networkx_graph(MDPG, mdpg_html)
    # for i, sdpg in enumerate(SDPG):
    #     sdpg_html = os.path.join(workspace,"sdpg_{:02d}_graph.html".format(i))
    #     GB.visualize_networkx_graph(sdpg, sdpg_html)
        
    # H = GB.serif_doc_to_mdp_graph(serif_doc)
    # GB.visualize_networkx_graph(H, os.path.join(workspace,"mpdg_graph.html"))

    # graphs = GB.serif_doc_to_mdp_graphs_by_sentence(serif_doc)
    # for i, H in enumerate(graphs):
    #     print("len of H is {}".format(len(H)))
    #     GB.visualize_networkx_graph(H, os.path.join(workspace, "mdpg_{:02d}_graph.html".format(i)))

    G = GB.serif_doc_to_mdp_graph(serif_doc)
    GB.visualize_networkx_graph(G, os.path.join(workspace, "mdpg_graph.html"))

    GB.initialize_token_to_mdp_node(serif_doc)
    for i, sentence in enumerate(serif_doc.sentences):
        H = GB.syntactic_dependency_parse_to_networkx(sentence, root_depth=3)
        I = GB.mdp_parse_for_sentence_to_networkx(sentence, root_depth=3)
        GB.visualize_networkx_graph(H, os.path.join(workspace,"sdpg_{:02d}_graph.html".format(i)))
        GB.visualize_networkx_graph(I, os.path.join(workspace,"mdpg_{:02d}_graph.html".format(i)))
        # note: arg order matters. node levels are preserved from 2nd arg
        J = nx.algorithms.operators.compose(I,H)
        GB.visualize_networkx_graph(J, os.path.join(workspace,"compose_{:02d}_graph.html".format(i)))
    



def main(args):
    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    for serifxml_path in serifxml_paths:
        print(serifxml_path)
        serif_doc = serifxml3.Document(serifxml_path)
        graph_view(serif_doc, args.workspace)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-w', '--workspace', type=str, required=True)
    args = parser.parse_args()

    main(args)
