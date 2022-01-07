CONDA=/nfs/mercury-13/u124/dzajic/miniconda3
CONDAENV=aida4

. ~/setup.conda.sh
conda activate $CONDA/envs/$CONDAENV

SGPM=/home/dzajic/dev/projects/rozonoyer/subgraph-pattern-matching/subgraph_pattern_matching
TEXTOPEN=/nfs/raid91/u10/developers/dzajic-ad/projects/text-group/text-open/src/python

# SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml/reuters_3003584698.xml
# SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/mds_appendix_annotations/serifxml/news.3.xml
SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/mds_appendix_annotations/serifxml/news.4.xml
WORKSPACE=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace

PYTHONPATH=$TEXTOPEN python $SGPM/extract_claims.py -i $SERIFXML -v
# PYTHONPATH=$TEXTOPEN python $SGPM/graph_viewer.py -i $SERIFXML -w $WORKSPACE
