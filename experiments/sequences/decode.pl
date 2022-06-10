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


foreach my $pattern_file (@patterns_by_config) {
    my @find_matches_jobs = ();

    (my $pattern_config = basename($pattern_file)) =~ s/\.[^.]+$//;

    my $grid_dir = "$matches_dir/${pattern_config}";

    my $create_grid_output_dirs = runjobs(
        [], "$JOB_NAME/$pattern_config/create_grid_output_dirs", { SCRIPT => 1 },
        "mkdir -p $grid_dir");

    for (my $i = 0; $i < $p->{NUM_BATCHES}; $i++) {
        my $find_matches_job = runjobs([$split_by_config_job], "$JOB_NAME/$pattern_config/$i/find_matches",
                                        {
                                            SGE_VIRTUAL_FREE => ["4G"]
                                        },
                               ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/decode.py -i $p->{INPUT_CORPUS} " .
                               "-p $pattern_file $p->{ISOMORPHISM} -m --stripe $i --num_batches $p->{NUM_BATCHES} " .
                               "-o $grid_dir/$i.pkl --config $pattern_config"]);
       push(@find_matches_jobs, $find_matches_job);
    }

    my $evaluate_matches_job = runjobs(\@find_matches_jobs, "$JOB_NAME/$pattern_config/evaluate_matches", { SGE_VIRTUAL_FREE => ["8G"] },
                                   ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/evaluate.py -i $p->{INPUT_CORPUS} " .
                                    "-m $grid_dir -e $p->{EVALUATION_CORPUS} -a $p->{ANNOTATION_SCHEME}"]);

}


# Execute the jobs now that scheduling has finished
endjobs();
