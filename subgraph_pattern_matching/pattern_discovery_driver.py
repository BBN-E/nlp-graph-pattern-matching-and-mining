import os, json
import argparse
import numpy as np

from local_pattern_finder import LocalPatternFinder, ParseTypes
from annotation.ingestion.event_ingester import EventIngester
from io.io_utils import serialize_pattern_graphs, deserialize_pattern_graphs
from clustering.distance_metrics import create_distance_matrix, approximate_graph_edit_distance
from clustering.cluster_graphs import cluster_digraphs
from clustering.generalize_patterns import get_pattern_from_clusters


distance_matrices_dir = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/pattern-discovery-4-19/combined_matrices"


def main(args):

    if not os.path.exists(args.output):
        os.mkdir(args.output)
    digraph_dir = os.path.join(args.output, "digraphs")

    # Use local pattern finder to ingest annotations and find config digraphs
    if args.save_digraphs:

        # ingest from a corpus
        aida_test_corpus = EventIngester().ingest_aida()

        # find local patterns on train set
        LPF = LocalPatternFinder()
        config_to_annotation_subgraphs = LPF.grid_search(annotations=aida_test_corpus.train_annotations, k_values=[3])

        if not os.path.exists(digraph_dir):
            os.mkdir(digraph_dir)

        index_to_config_key = []
        for i, (key, digraph_list) in enumerate(config_to_annotation_subgraphs.items()):
            index_to_config_key.append(key)
            json_dump = serialize_pattern_graphs(digraph_list)

            with open(digraph_dir + "/digraphs_{}.json".format(i), 'w') as f:
                f.write(json_dump)

        # TODO: ParseTypes not json serializable, figure out an encoding
        with open(os.path.join(args.output, "index_to_config.json"), 'w') as index_to_config_f:
            json.dump(index_to_config_key, index_to_config_f, default=str)

        return

    distance_matrices = {}
    config_to_annotation_subgraphs = {}

    if args.load_distance_matrices:
        # load distance matrices and saved digraphs
        with open(os.path.join(args.output, "index_to_config.json")) as index_to_config_f:
            index_to_config_key = json.load(index_to_config_f)

        for index, list_key in enumerate(index_to_config_key):

            list_key[1] = tuple(list_key[1])
            key = tuple(list_key)

            digraph_path = os.path.join(digraph_dir, "digraphs_{}.json".format(index))
            digraph_list = deserialize_pattern_graphs(digraph_path, is_file_path=True)
            config_to_annotation_subgraphs[key] = digraph_list

            distance_matrix_path = os.path.join(distance_matrices_dir, "combined_distance_matrix_digraphs_{}.json.np".format(index))
            with open(distance_matrix_path, 'rb') as f:
                distance_matrix = np.load(f)
                # print(distance_matrix)
                distance_matrices[key] = distance_matrix
    else:
        # apply distance function on train set data
        for key, digraph_list in enumerate(config_to_annotation_subgraphs.items()):
            distance_matrix = create_distance_matrix(digraph_list)
            distance_matrices[key] = distance_matrix

    # cluster local patterns on train set, create representative pattern from each cluster
    for key, distance_matrix in distance_matrices.items():
        print(key)
        # skip empty distance matrices
        if not np.any(distance_matrix):
            continue
        labels = cluster_digraphs(config_to_annotation_subgraphs[key], distance_matrix)
        cluster_num_to_cluster_pattern = get_pattern_from_clusters(config_to_annotation_subgraphs[key], distance_matrix, labels)
        print(cluster_num_to_cluster_pattern)

    # TODO: apply new patterns to hold out set, compare to existing annotations


if __name__ == '__main__':
    '''
    PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python 
    python3 
    /nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching/pattern_discovery_driver.py 
    --output /nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/pattern-discovery-4-18 
    --save_digraphs
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('--load_distance_matrices', action='store_true', help="load preexisting distance matrices")
    parser.add_argument('--save_digraphs', action='store_true', help='stop prematurely and save digraphs to use with runjobs script')
    parser.add_argument('-o', '--output', type=str, required=True, help='output directory to store patterns and intermediate files')
    args = parser.parse_args()

    main(args)