
use strict;
use warnings;

my $SUBGRAPH_PATTERN_MATCHING_RELEASE = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching";
my $SUBGRAPH_PATTERN_MATCHING_PYTHONPATH = "$SUBGRAPH_PATTERN_MATCHING_RELEASE/python/subgraph_pattern_matching";

my $PYTHON3= "env PYTHONPATH=/nfs/raid83/u13/caml/users/mselvagg_ad/text-open-2/src/python:$SUBGRAPH_PATTERN_MATCHING_PYTHONPATH " .
             "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python";


my $INPUT_CORPUS = "/nfs/raid83/u13/caml/users/mselvagg_ad/data/conll/eng/eng.testb.xml -s";
my $PATTERNS_PATH = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/experiments/expts/5-16-2022-ungeneralized-conll-v5/all_patterns.json";

my @ISOMORPHISM_CONFIG = ("isomorphism", "monomorphism");

my $EVALUATION_CORPUS = "CONLL_ENGLISH";
my $NUM_BATCHES = 500;

my $ANNOTATION_SCHEME = "IDENTIFICATION_CLASSIFICATION";

return {
    PYTHON3 => $PYTHON3,
    SUBGRAPH_PATTERN_MATCHING_RELEASE => $SUBGRAPH_PATTERN_MATCHING_RELEASE,
    SUBGRAPH_PATTERN_MATCHING_PYTHONPATH => $SUBGRAPH_PATTERN_MATCHING_PYTHONPATH,
    EVALUATION_CORPUS => $EVALUATION_CORPUS,
    NUM_BATCHES => $NUM_BATCHES,
    INPUT_CORPUS => $INPUT_CORPUS,
    PATTERNS_PATH => $PATTERNS_PATH,
    ISOMORPHISM_CONFIG => \@ISOMORPHISM_CONFIG,
    ANNOTATION_SCHEME => $ANNOTATION_SCHEME
};
