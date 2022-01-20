import os, json
import argparse
import networkx as nx
from collections import defaultdict

import serifxml3

from constants import NodeTypes, EdgeTypes, \
    NodeAttrs, TokenNodeAttrs, ModalNodeAttrs, \
    EdgeAttrs, SyntaxEdgeAttrs, ModalEdgeAttrs

from graph_builder import GraphBuilder
from graph_viewer import GraphViewer

def graph_view(serif_doc, workspace):
    GB = GraphBuilder()
    GV = GraphViewer()

    G = GB.modal_dependency_parse_to_networkx(serif_doc)
    GV.prepare_mdp_networkx_for_visualization(G)
    GV.visualize_networkx_graph(G, os.path.join(workspace,"mdp_graph.html"))

    for i, sentence in enumerate(serif_doc.sentences):
        H = GB.syntactic_dependency_parse_to_networkx(sentence)
        GV.prepare_sdp_networkx_for_visualization(H, root_level=3)
        GV.visualize_networkx_graph(H, os.path.join(workspace,"sdp_{:02d}_graph.html".format(i)))
        F = GV.filter_mdp_networkx_by_sentence(G, H)
        GV.visualize_networkx_graph(F, os.path.join(workspace,"mdp_{:02d}_graph.html".format(i)))
        J = nx.algorithms.operators.compose(F,H)
        GV.visualize_networkx_graph(J, os.path.join(workspace,"compose_{:02d}_graph.html".format(i)))


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
