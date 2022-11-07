
use strict;
use warnings;

my $SUBGRAPH_PATTERN_MATCHING_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching";
my $GSPAN = "/home/dzajic/dev/projects/graph/gSpan";
my $NEURAL_SUBGRAPH_LEARNING_GNN = "/nfs/raid83/u13/caml/users/mselvagg_ad/spminer";
my $TEXT_OPEN_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python";
my $SUBGRAPH_PATTERN_MATCHING_PYTHONPATH = "$SUBGRAPH_PATTERN_MATCHING_RELEASE/python/subgraph_pattern_matching";

my $PYTHON3= "env PYTHONPATH=$TEXT_OPEN_RELEASE:$SUBGRAPH_PATTERN_MATCHING_PYTHONPATH:$GSPAN:$NEURAL_SUBGRAPH_LEARNING_GNN " .
    "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/py39/bin/python";

# CONLL_ENGLISH, ACE_ENGLISH, TACRED
my $ANNOTATION_CORPUS = "AIDA_CLAIMS";
my $ANNOTATION_CATEGORIES = "$SUBGRAPH_PATTERN_MATCHING_RELEASE/subgraph_pattern_matching/annotation/ontologies/conll_ner.txt";
my $SPLIT_BY_CATEGORY = 0;

# grid search parameters
my @K_VALUES = (2);
my @SEARCH_DIRECTIONS = ("BOTH");
my @PARSE_TYPE_COMBINATIONS = ("AMR DP", "DP", "AMR");

# leave undefined if not using MajorityWins or CentralGraph strategy
# DBSCAN, IdenticalStructures
my $CLUSTER_ALGORITHM;
my $NUM_BATCHES = 1;

# Ungeneralized, MajorityWins, CentralGraph, GSpan, SPMiner
my $GENERALIZATION_STRATEGY = "SPMiner";

# GSpan parameters. Irrelevant if not using GSpan strategy
my $MIN_SUPPORT_VECTORS = "--min_support 10";
my $MIN_NUM_VERTICES = "--min_num_vertices 10";
my $MAX_NUM_VERTICES; # = "--max_num_vertices";


my @SPMINER_CONFIGURATIONS = ("$SUBGRAPH_PATTERN_MATCHING_RELEASE/experiments/templates/spminer_nlp_config_test.json");


return {
    PYTHON3 => $PYTHON3,
    SUBGRAPH_PATTERN_MATCHING_RELEASE => "$SUBGRAPH_PATTERN_MATCHING_RELEASE/subgraph_pattern_matching",
    SUBGRAPH_PATTERN_MATCHING_PYTHONPATH => $SUBGRAPH_PATTERN_MATCHING_PYTHONPATH,
    ANNOTATION_CORPUS => $ANNOTATION_CORPUS,
    K_VALUES => \@K_VALUES,
    SEARCH_DIRECTIONS => \@SEARCH_DIRECTIONS,
    PARSE_TYPE_COMBINATIONS => \@PARSE_TYPE_COMBINATIONS,
    CLUSTER_ALGORITHM => $CLUSTER_ALGORITHM,
    NUM_BATCHES => $NUM_BATCHES,
    SPLIT_BY_CATEGORY => $SPLIT_BY_CATEGORY,
    ANNOTATION_CATEGORIES => $ANNOTATION_CATEGORIES,
    GENERALIZATION_STRATEGY => $GENERALIZATION_STRATEGY,
    MIN_SUPPORT_VECTORS => $MIN_SUPPORT_VECTORS,
    MIN_NUM_VERTICES => $MIN_NUM_VERTICES,
    MAX_NUM_VERTICES => $MAX_NUM_VERTICES,
    SPMINER_CONFIGURATIONS => \@SPMINER_CONFIGURATIONS
};
