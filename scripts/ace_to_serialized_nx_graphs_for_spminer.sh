env PYTHONPATH=/nfs/raid66/u11/users/brozonoy-ad/text-open/src/python:/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/ \
/nfs/raid83/u13/caml/users/mselvagg_ad/miniconda/envs/scratch/bin/python \
/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/subgraph_pattern_matching/local_pattern_finder.py \
--annotation_corpus ACE_ENGLISH \
-k 5 \
--parse_types DP AMR \
--search_direction BOTH \
--output /nfs/raid66/u11/users/brozonoy-ad/spminer/data/ace_english.json \
--annotation_category all_categories \
--create_dataset_for_spminer