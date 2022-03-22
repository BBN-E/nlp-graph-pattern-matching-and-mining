CONDA=/nfs/mercury-13/u124/dzajic/miniconda3
CONDAENV=aida4

. ~/setup.conda.sh
conda activate $CONDA/envs/$CONDAENV

SGPM=/home/dzajic/dev/projects/rozonoyer/subgraph-pattern-matching/subgraph_pattern_matching
TEXTOPEN=/nfs/raid91/u10/developers/dzajic-ad/projects/text-group/text-open/src/python

# SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml/reuters_3003584698.xml
# SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/mds_appendix_annotations/serifxml/news.3.xml
# SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/mds_appendix_annotations/serifxml/news.4.xml
SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/subgraph-pattern-matching/mds_appendix_annotations/serifxml.debug/news.4.xml
# SERIFXML=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/serifxml/news.4.xml
# SERIFXML=/nfs/mercury-13/u124/dzajic/aida/mtdp/workspace/L0C04958H.rsd.xml
# SERIFXML=/nfs/mercury-13/u124/dzajic/aida/mtdp/workspace/L0C04958I.rsd.xml
# SERIFXML=/nfs/mercury-13/u124/dzajic/aida/mtdp/output/mtdp.LDC2021E11.2022-01-14.nlplingo.small/L0C049DQH.mt.xml
# SERIFXML=/nfs/mercury-13/u124/dzajic/aida/mtdp/output/mtdp.LDC2021E11.20220117/L0C04958D.rsd.xml
# WORKSPACE=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/html

DOC=L0C04958I
SERIFXML=/nfs/mercury-13/u124/dzajic/aida/mtdp/output/mtdp.LDC2021E11.20220117/$DOC.rsd.xml
WORKSPACE=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/html.$DOC

DOC=cnn_3000084273
SERIFXML=/nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/modal.serifxml.with_amr/$DOC.xml
WORKSPACE=/nfs/raid91/u10/developers/dzajic-ad/projects/rozonoyer/subgraph-pattern-matching/workspace/html.$DOC


# PYTHONPATH=$TEXTOPEN python $SGPM/extract_claims.py -i $SERIFXML -v
mkdir -p $WORKSPACE
PYTHONPATH=$TEXTOPEN:$SGPM python $SGPM/utils/test_graph_viewer.py -i $SERIFXML -w $WORKSPACE
