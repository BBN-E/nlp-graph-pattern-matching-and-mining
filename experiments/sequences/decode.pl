#!/usr/bin/env perl

use strict;
use warnings;

use lib "/d4m/ears/releases/runjobs4/R2020_05_20/lib/";
use runjobs4;

# Standard libraries
use File::Basename;
use FindBin qw($Bin $Script);
use Getopt::Long;
use Digest::MD5 qw(md5_hex);

my $p;
BEGIN {
    (my $param_file = "$Bin/$Script") =~ s/\.pl$/.defines.pl/;
    my $user_params = do $param_file;
    if (!defined $user_params) {
        die "Unable to parse '$param_file': $@\n" if $@;
        die "Unable to load '$param_file': $!\n" if $!;
    }
    $p = $user_params;
}

my $JOB_NAME = "decoding";

# Process our arguments; pass the rest through to runjobs.
Getopt::Long::Configure("pass_through");
GetOptions(
    "job_name=s"         => \$JOB_NAME,
    );
Getopt::Long::Configure("no_pass_through");
die if $Getopt::Long::error;
die "Expected --job_name" if !defined($JOB_NAME);

############################################################################
# Job Scheduling
############################################################################

# Initializing runjobs
my ($exp_root, $exp) = startjobs(
    batch_queue     => 'cpunodes',
    local_dir       => '/export/u10',
);

# Create our output directories
my $expt_dir = "$exp_root/expts/$JOB_NAME/";
my $matches_dir = "$expt_dir/matches";
my $config_splits = "$expt_dir/config_splits";

my $create_output_dirs = runjobs(
    [], "$JOB_NAME/create_output_dirs", { SCRIPT => 1 },
    "mkdir -p $matches_dir $config_splits");

my $split_by_config_job = runjobs(
    [$create_output_dirs], "$JOB_NAME/split_by_config", { SGE_VIRTUAL_FREE => ["4G"]},
    "$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/evaluation/split_by_config.py -i $p->{PATTERNS_PATH} -o $config_splits");

dojobs();

my @patterns_by_config = glob ("$config_splits/*");

my @find_matches_jobs = ();

foreach my $pattern_file (@patterns_by_config) {
    (my $pattern_config = basename($pattern_file)) =~ s/\.[^.]+$//;

    for (my $i = 0; $i < $p->{NUM_BATCHES}; $i++) {
        my $find_matches_job = runjobs([$split_by_config_job], "$JOB_NAME/find_matches/$pattern_config/$i",
                                        {
                                            SGE_VIRTUAL_FREE => ["4G"]
                                        },
                               ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/decode.py -i $p->{INPUT_CORPUS} " .
                               "-p $p->{PATTERNS_PATH} -m --stripe $i --num_batches $p->{NUM_BATCHES} -o $matches_dir/${pattern_config}_$i.pkl " .
                               "--config $pattern_config"]);
       push(@find_matches_jobs, $find_matches_job);
    }
}

my $evaluate_matches_job = runjobs(\@find_matches_jobs, "$JOB_NAME/evaluate_matches", { SGE_VIRTUAL_FREE => ["8G"] },
                                   ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/evaluate.py -i $p->{INPUT_CORPUS} -m $matches_dir -e $p->{EVALUATION_CORPUS}"]);

# Execute the jobs now that scheduling has finished
endjobs();
