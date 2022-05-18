
use strict;
use warnings;

my $SUBGRAPH_PATTERN_MATCHING_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching";
my $GSPAN = "/home/dzajic/dev/projects/graph/gSpan";

my $PYTHON3= "env PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python:$SUBGRAPH_PATTERN_MATCHING_RELEASE:$GSPAN " .
    "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python";

# CONLL_ENGLISH, ACE_ENGLISH
my $ANNOTATION_CORPUS = "CONLL_ENGLISH";
my $ANNOTATION_CATEGORIES = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/4-29-2022-test-categories/annotation_categories.list";
# my $ANNOTATION_CATEGORIES = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/5-2-22-specific-ACE-types/annotation_categories.list";
my $SPLIT_BY_CATEGORY = 1;

# grid search parameters
my @K_VALUES = (6);
my @SEARCH_DIRECTIONS = ("UP", "DOWN", "BOTH");
my @PARSE_TYPE_COMBINATIONS = ("AMR DP", "AMR", "DP");

# DBSCAN, IdenticalStructures, Centroid Graph
my $CLUSTER_ALGORITHM;

# Ungeneralized, MajorityWins, CentralGraph, GSpan
my $GENERALIZATION_STRATEGY = "MajorityWins";
my $NUM_BATCHES = 50;

# GSpan parameters. Irrelevant if not using GSpan strategy
my $MIN_SUPPORT_VECTORS = "--min_support 40";
my $MIN_NUM_VERTICES = "--min_num_vertices 7";
my $MAX_NUM_VERTICES; # = "--max_num_vertices";

# set this to "--all_attrs" if using Ungeneralized strategy
my $ALL_ATTRS = "--all_attrs";


return {
    PYTHON3 => $PYTHON3,
    SUBGRAPH_PATTERN_MATCHING_RELEASE => $SUBGRAPH_PATTERN_MATCHING_RELEASE,
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
    MAX_NUM_VERTICES => $MAX_NUM_VERTICES
    ALL_ATTRS => $ALL_ATTRS
};
