
use strict;
use warnings;

my $SUBGRAPH_PATTERN_MATCHING_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching";

my $PYTHON3= "env PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python:$SUBGRAPH_PATTERN_MATCHING_RELEASE " .
             "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python";

my $ANNOTATION_CORPUS = "AIDA_TEST";

# grid search parameters
my @K_VALUES = (1,2);
my @SEARCH_DIRECTIONS = ("UP", "DOWN", "BOTH");
my @PARSE_TYPE_COMBINATIONS = ("MDP", "DP", "DP MDP");

my $CLUSTER_ALGORITHM = "";

my $NUM_BATCHES = 50;

return {
    PYTHON3 => $PYTHON3,
    SUBGRAPH_PATTERN_MATCHING_RELEASE => $SUBGRAPH_PATTERN_MATCHING_RELEASE,
    ANNOTATION_CORPUS => $ANNOTATION_CORPUS,
    K_VALUES => \@K_VALUES,
    SEARCH_DIRECTIONS => \@SEARCH_DIRECTIONS,
    PARSE_TYPE_COMBINATIONS => \@PARSE_TYPE_COMBINATIONS,
    CLUSTER_ALGORITHM => $CLUSTER_ALGORITHM,
    NUM_BATCHES => $NUM_BATCHES
};
