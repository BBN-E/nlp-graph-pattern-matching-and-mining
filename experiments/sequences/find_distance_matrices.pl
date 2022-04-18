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

my $JOB_NAME;
my $INPUT_DIR = "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/pattern-discovery-4-18/digraphs";
my $PYTHON3= "/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python";
my $SCRIPT_LOCATION= "/nfs/raid83/u13/caml/users/mselvagg_ad/subgraph-pattern-matching/subgraph_pattern_matching/clustering";
my $num_batches = 50;

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
my $batch_dir = "$expt_dir/batches";
my $out_dir = "$expt_dir/combined_matrices";

my $create_output_dirs = runjobs(
    [], "$JOB_NAME/create_output_dirs", { SCRIPT => 1 },
    "mkdir -p $batch_dir $out_dir");


opendir(DH, "$INPUT_DIR");
my @graph_files = readdir(DH);
closedir(DH);

foreach my $graph_file (@graph_files)
{
    next if($graph_file =~ /^\.$/);
    next if($graph_file =~ /^\.\.$/);

    my @dist_matrix_batch_jobs = ();

    my $batch_subdir = "$batch_dir/$graph_file";
    my $create_batch_output_dir = runjobs([$create_output_dirs], "$JOB_NAME/$graph_file/create_batch_output", { SCRIPT => 1 }, "mkdir -p $batch_subdir");

    for (my $i = 0; $i < $num_batches; $i++) {

        my $dist_matrix_batch_job = runjobs([$create_batch_output_dir], "$JOB_NAME/dist_matrix_batch/$graph_file/$i",
                                ["$PYTHON3 $SCRIPT_LOCATION/distance_matrix_batch.py --num_batches $num_batches " .
                                 "--stripe $i --output_file_path $batch_dir/$graph_file/dist_matrix_split_$i --input_graphs $INPUT_DIR/$graph_file"]);
        push(@dist_matrix_batch_jobs, $dist_matrix_batch_job);
    }

    my $combine_matrices_job = runjobs(\@dist_matrix_batch_jobs, "$JOB_NAME/$graph_file/combine_matrices",
                                       {SGE_VIRTUAL_FREE => ["4G", "8G"]},
                                      ["$PYTHON3 $SCRIPT_LOCATION/combine_distance_matrices.py --num_batches $num_batches " .
                                       "--input_dir_path $batch_subdir --output_file_path $out_dir/combined_distance_matrix_$graph_file.np"]);
}

# Execute the jobs now that scheduling has finished
endjobs();
