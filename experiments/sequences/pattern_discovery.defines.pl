
use strict;
use warnings;

my $SUBGRAPH_PATTERN_MATCHING_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching";

my $PYTHON3= "env PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python:$SUBGRAPH_PATTERN_MATCHING_RELEASE " .
             "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python";

my $ANNOTATION_CORPUS = "ACE_ENGLISH";
my $ANNOTATION_CATEGORIES = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/5-2-22-specific-ACE-types/annotation_categories.list";
my $SPLIT_BY_CATEGORY = 0;

# grid search parameters
my @K_VALUES = (2,3);
my @SEARCH_DIRECTIONS = ("BOTH");
my @PARSE_TYPE_COMBINATIONS = ("AMR", "AMR DP");

my $CLUSTER_ALGORITHM;

my $NUM_BATCHES = 50;


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
    ANNOTATION_CATEGORIES => $ANNOTATION_CATEGORIES
};
