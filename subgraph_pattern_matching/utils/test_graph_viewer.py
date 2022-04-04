import os, json
import argparse
import networkx as nx
from collections import defaultdict
import ast
import serifxml3
import penman
from penman import surface
from penman.surface import Alignment

from constants.common.types.node_types import NodeTypes
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from constants.common.types.edge_types import EdgeTypes
from constants.common.attrs.edge.edge_attrs import EdgeAttrs
from constants.common.attrs.edge.syntax_edge_attrs import SyntaxEdgeAttrs
from constants.common.attrs.edge.modal_edge_attrs import ModalEdgeAttrs

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
        GV.prepare_sdp_networkx_for_visualization(H, root_level=4)
        GV.visualize_networkx_graph(H, os.path.join(workspace,"sdp_{:02d}_graph.html".format(i)))
        K = GB.amr_parse_to_networkx(sentence)
        GV.prepare_amr_networkx_for_visualization(K, root_level=0)
        GV.visualize_networkx_graph(K, os.path.join(workspace,"amr_{:02d}_graph.html".format(i)),
                                    sentence_text=sentence.text)

        N = GB.token_to_networkx(sentence)
        GV.prepare_tok_networkx_for_visualization(N, root_level=0)
        GV.visualize_networkx_graph(N, os.path.join(workspace,"tok_{:02d}_graph.html".format(i)))

        K_max_level = GV.get_max_level(K)
        N_max_level = GV.get_max_level(N)
        GV.invert_node_levels(K)
        GV.adjust_level(K, N_max_level+1)

        O = nx.algorithms.compose(K,N)
        GV.visualize_networkx_graph(O, os.path.join(workspace,"amr_tok_{:02d}_graph.html".format(i)),
                                    sentence_text=sentence.text)

        F = GV.filter_mdp_networkx_by_sentence(G, H)
        GV.visualize_networkx_graph(F, os.path.join(workspace,"mdp_{:02d}_graph.html".format(i)))
        # J = nx.algorithms.operators.compose(F,K)
        # GV.visualize_networkx_graph(J, os.path.join(workspace,"mdp_amr_compose_{:02d}_graph.html".format(i)))
        L = nx.algorithms.operators.compose(F,H)
        GV.visualize_networkx_graph(L, os.path.join(workspace,"mdp_sdp_compose_{:02d}_graph.html".format(i)))
        # M = nx.algorithms.operators.compose(L,K)
        # GV.visualize_networkx_graph(M, os.path.join(workspace,"all_compose_{:02d}_graph.html".format(i)))


def amr_print_interesting_alignments(serif_doc, ORG):
    for i, sent in enumerate(serif_doc.sentences):
        amr_parse = sent.amr_parse
        g = penman.decode(amr_parse._amr_string)
        alignments = surface.alignments(g)
        for key in alignments.keys():
            alignment = alignments[key]
            if len(alignment.indices) > 2:
                ORG.write(f"* Document {serif_doc.docid} Sentence {i} Alignment {key} {alignment}\n")
                ORG.write(f"{sent.text}\n")
                for index in alignment.indices:
                    ORG.write(f"index {index} token {sent.token_sequence[index].text}\n")
                included_text = " ".join([x.text for x in sent.token_sequence[alignment.indices[0]:alignment.indices[-1]+1]])
                ORG.write(f"{included_text}\n")
                

def amr_print(serif_doc, ORG):
    ORG.write(f"* Document {serif_doc.docid}\n")
    print(serif_doc.docid)
    for i, sent in enumerate(serif_doc.sentences):
        amr_parse = sent.amr_parse
        ORG.write(f"** Sentence {i}\n")
        ORG.write(f"{sent.text}\n")
        ORG.write(f"{amr_parse._amr_string}\n")
        ORG.write("*** Tokens\n")
        for i, t in enumerate(sent.text.split(' ')):
            ORG.write(f"{i} {t}\n")
        g = penman.decode(amr_parse._amr_string)
        t = penman.parse(amr_parse._amr_string)
        ORG.write("*** graph\n")
        ORG.write(f"{penman.encode(g)}\n")
        ORG.write("*** graph nodes\n")
        for triple in g.triples:
            ORG.write(f"**** {triple}\n")
            ORG.write(f"{g.epidata[triple]}\n")
        ORG.write("*** graph alignments\n")
        alignments = surface.alignments(g)
        for key in alignments.keys():
            ORG.write(f"{key} {alignments[key].indices} L={len(alignments[key].indices)}\n")
        ORG.write("*** tree\n")
        ORG.write(f"{penman.format(t)}\n")
        ORG.write("*** Nodes\n")
        for node in t.nodes():
            var = node[0]
            content = dict(node[1])
            keys = [x for x in content.keys() if type(content[x]) == str and x != '/']
            ORG.write(f"{var} {content['/']} {keys}\n")
        ORG.write("*** Nodes\n")
        amr_print_node(ORG, amr_parse.root, set())

def amr_print_node (ORG, node, previously_seen_nodes, amr_rel="root", depth=0):
    penman_tree = dict(json.loads(node._penman_tree)[1])

    ORG.write("  " * depth)
    if node in previously_seen_nodes:
        ORG.write(f"X {amr_rel} {node.varname} {node.content}\n")
        return
    else:
        ORG.write(f"{amr_rel} {node.varname} {node.content} {penman_tree}\n")

    previously_seen_nodes.add(node)
    if node._outgoing_amr_rels is not None:
        amr_rels = ast.literal_eval(node._outgoing_amr_rels)
        for child, amr_rel in zip(node._children, amr_rels):
            amr_print_node (ORG, child, previously_seen_nodes, amr_rel=amr_rel, depth=depth+1)
    else:
        for child in node._children:
            amr_print_node (ORG, child, previously_seen_nodes, depth=depth+1)
    

def main(args):
    if args.list:
        with open(args.input, 'r') as f:
            serifxml_paths = [l.strip() for l in f.readlines() if l.strip()]
    else:
        serifxml_paths = [args.input]

    org = os.path.join(args.workspace,"amr.org")
    ORG = open(org,'w')

    for serifxml_path in serifxml_paths:
        print(serifxml_path)
        serif_doc = serifxml3.Document(serifxml_path)
        graph_view(serif_doc, args.workspace)
        # amr_print(serif_doc, ORG)
        # amr_print_interesting_alignments(serif_doc, ORG)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, required=True)
    parser.add_argument('-l', '--list', action='store_true', help='input is list of serifxmls rather than serifxml path')
    parser.add_argument('-w', '--workspace', type=str, required=True)
    args = parser.parse_args()

    main(args)
