CONDA=/nfs/mercury-13/u124/dzajic/miniconda3
CONDAENV=aida4

. ~/setup.conda.sh
conda activate $CONDA/envs/$CONDAENV

SGPM=/home/dzajic/dev/projects/rozonoyer/subgraph-pattern-matching/subgraph_pattern_matching
TEXTOPEN=/nfs/raid91/u10/developers/dzajic-ad/projects/text-group/text-open/src/python

DOC=foxnews_71348028
SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml.with_amr/$DOC.xml
WORKSPACE=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/html.$DOC

# SERIFXML_LIST=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/serifxml_with_amr.list

mkdir -p $WORKSPACE
PYTHONPATH=$TEXTOPEN:$SGPM python $SGPM/view_utils/view_graphs.py -i $SERIFXML -w $WORKSPACE
# PYTHONPATH=$TEXTOPEN:$SGPM python $SGPM/utils/test_graph_viewer.py -l -i $SERIFXML_LIST -w $WORKSPACE
