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

my $JOB_NAME = "pattern_discovery";

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

my @setup_jobs = ();

my @annotations;

if ($p->{SPLIT_BY_CATEGORY}) {
    # retrieve categories if no category file provided
    my $annotation_categories_path = $p->{ANNOTATION_CATEGORIES};

    if (not($annotation_categories_path)) {
        $annotation_categories_path = "$expt_dir/annotation_categories.list";
        my $get_annotated_categories_job = runjobs([], "$JOB_NAME/get_annotated_categories", {SGE_VIRTUAL_FREE => ["4G", "8G"]},
                                                    ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/runjobs_helper_scripts/get_annotation_categories.py " .
                                                     "--annotation_corpus $p->{ANNOTATION_CORPUS} --output $annotation_categories_path"]);
        push(@setup_jobs, $get_annotated_categories_job);
        dojobs();
    }
    my $FH;
    unless (open($FH, '<', $annotation_categories_path)) {
       print STDERR "Could not open file '$annotation_categories_path': $!\n";
       return undef;
    }
    chomp(@annotations = <$FH>);
    close($FH);
} else {
    @annotations = ("all_categories");
}

#"--all_attrs" if not using clustering
my $all_attrs = "--all_attrs";
if ($p->{CLUSTER_ALGORITHM}) {
    $all_attrs = " ";
}

my @spminer_configs = @{$p->{SPMINER_CONFIGURATIONS}};
my $config_size = scalar @spminer_configs;
if ($config_size <= 0) {
    $config_size = 1;
}

my $i;
for ($i=0; $i<$config_size; ++$i) {
    my $spm_config_path = $spminer_configs[$i];

    my $grid_config_dir;
    if ($config_size > 1 and $p->{GENERALIZATION_STRATEGY} == "SPMiner") {
        $grid_config_dir = "$expt_dir/spminer_config_$i";
    } else {
        $grid_config_dir = "$expt_dir/grid_config";
    }

    my $create_config_dir = runjobs([], "$JOB_NAME/$i/create_category_dir",
                                    { SCRIPT => 1 },  "mkdir -p $grid_config_dir $grid_config_dir/visualizations");
    push(@setup_jobs, $create_config_dir);

    my @generalized_patterns_jobs = ();

    foreach my $category (@annotations) {

        my @category_setup_jobs = @setup_jobs;
        my $category_formatted = "$category";
        $category_formatted =~ s/(\:|\/)/_/g;
        my $category_dir = "$grid_config_dir/$category_formatted";
        if ($p->{SPLIT_BY_CATEGORY}) {
            my $create_category_dir = runjobs(\@setup_jobs, "$JOB_NAME/$i/$category_formatted/create_category_dir",
                                          { SCRIPT => 1 },  "mkdir -p $category_dir");
            push(@category_setup_jobs, $create_category_dir);
        }

        foreach my $k (@{$p->{K_VALUES}}) {
            foreach my $parse_types (@{$p->{PARSE_TYPE_COMBINATIONS}}) {
                foreach my $search_direction (@{$p->{SEARCH_DIRECTIONS}}) {

                    my $config = "$k-$search_direction-$parse_types";
                    $config =~ tr/ /_/ds;

                    my $grid_config_dir = "$category_dir/$config";
                    my $serialized_local_patterns_path = "$grid_config_dir/patterns.json";

                    my $experiment_prefix = "$JOB_NAME/$i/$category_formatted/$config";


                    my $find_local_patterns_job = runjobs(\@category_setup_jobs, "$experiment_prefix/find_local_patterns", {SGE_VIRTUAL_FREE => ["4G", "8G", "32G"]},
                                                          ["mkdir -p $grid_config_dir"],
                                                          ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/local_pattern_finder.py --annotation_corpus $p->{ANNOTATION_CORPUS} " .
                                                           "-k $k --parse_types $parse_types --search_direction $search_direction --output $serialized_local_patterns_path " .
                                                           "--annotation_category $category $all_attrs"]);

                    # Only do clustering if cluster algorithm is set
                    if ($p->{CLUSTER_ALGORITHM}) {
                        my @dist_matrix_batch_jobs = ();

                        my $batch_subdir = "$grid_config_dir/dist_matrices";
                        my $create_batch_output_dir = runjobs([$find_local_patterns_job], "$experiment_prefix/create_batch_output", { SCRIPT => 1 }, ["mkdir -p $batch_subdir"]);

                        for (my $i = 0; $i < $p->{NUM_BATCHES}; $i++) {

                            my $dist_matrix_batch_job = runjobs([$create_batch_output_dir], "$experiment_prefix/dist_matrix_batch/$i", {SGE_VIRTUAL_FREE => ["4G", "8G"]},
                                                    ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/clustering/distance_matrix_batch.py --num_batches $p->{NUM_BATCHES} " .
                                                     "--stripe $i --output_file_path $batch_subdir/dist_matrix_split_$i --input_graphs $serialized_local_patterns_path"]);
                            push(@dist_matrix_batch_jobs, $dist_matrix_batch_job);
                        }

                        my $combine_matrices_job = runjobs(\@dist_matrix_batch_jobs, "$experiment_prefix/combine_matrices",
                                                          {SGE_VIRTUAL_FREE => ["8G", "16G"]},
                                                          ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/clustering/combine_distance_matrices.py --num_batches $p->{NUM_BATCHES} " .
                                                           "--input_dir_path $batch_subdir --output_file_path $grid_config_dir/combined_distance_matrix.np"]);

                        my $clustering_job = runjobs([$combine_matrices_job], "$experiment_prefix/cluster_graphs", {SGE_VIRTUAL_FREE => ["4G"]},
                                                     ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/clustering/cluster_graphs.py  " .
                                                     "--distance_matrix $grid_config_dir/combined_distance_matrix.np " .
                                                      "--output $grid_config_dir/labels.json --cluster_option $p->{CLUSTER_ALGORITHM} "]);

                        my $generalize_patterns_job = runjobs([$clustering_job], "$experiment_prefix/generalize_patterns", {SGE_VIRTUAL_FREE => ["4G"]},
                                     ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/generalize_patterns.py  " .
                                     "--local_patterns_json $serialized_local_patterns_path --distance_matrix $grid_config_dir/combined_distance_matrix.np " .
                                      "--labels $grid_config_dir/labels.json --output $grid_config_dir/patterns --strategy $p->{GENERALIZATION_STRATEGY} " .
                                      "$p->{MIN_SUPPORT_VECTORS} $p->{MIN_NUM_VERTICES} $p->{MAX_NUM_VERTICES}"]);
                        push(@generalized_patterns_jobs, $generalize_patterns_job);
                    } else {
                        my $generalize_patterns_job = runjobs([$find_local_patterns_job], "$experiment_prefix/generalize_patterns", {SGE_VIRTUAL_FREE => ["4G"]},
                                         ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/generalize_patterns.py  " .
                                         "--local_patterns_json $serialized_local_patterns_path --output $grid_config_dir/patterns --strategy $p->{GENERALIZATION_STRATEGY} " .
                                         "$p->{MIN_SUPPORT_VECTORS} $p->{MIN_NUM_VERTICES} $p->{MAX_NUM_VERTICES} --spminer_config $spm_config_path"]);
                        push(@generalized_patterns_jobs, $generalize_patterns_job);
                    }
                }
            }
        }
    }

    my $list_pattern_paths_job = runjobs(\@generalized_patterns_jobs, "$JOB_NAME/$i/list_pattern_paths", { SCRIPT => 1},
                                       ["ls $grid_config_dir/*/*/patterns/patterns_cluster_*.json > $grid_config_dir/pattern_paths.list"]);

    my $combine_pattern_lists_job = runjobs([$list_pattern_paths_job], "$JOB_NAME/$i/combine_pattern_paths",
                                           {SCRIPT => 1, SGE_VIRTUAL_FREE => ["4G"]},
                                           ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/runjobs_helper_scripts/combine_pattern_jsons.py " .
                                            "--input_list $grid_config_dir/pattern_paths.list --output $grid_config_dir/all_patterns.json"]);

    my $visualize_all_patterns_job = runjobs([$combine_pattern_lists_job], "$JOB_NAME/$i/visualize_patterns",
                                           {SCRIPT => 1},
                                           ["$p->{PYTHON3} $p->{SUBGRAPH_PATTERN_MATCHING_RELEASE}/view_utils/quick_visualize.py " .
                                            "--visualization_dir $grid_config_dir/visualizations --generalized_patterns $grid_config_dir/all_patterns.json"]);
}



# Execute the jobs now that scheduling has finished
endjobs();
