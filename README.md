# subgraph-pattern-matching

Using subgraph pattern matching over compositions of multifarious linguistic parses to extract meaningful knowledge elements. 

For pattern matching, requires `networkx==2.8`, `tqdm`, `pyvis` and `penman` (for matching over AMR graphs) to be installed in the environment.

For pattern mining with SPMiner, see the requirements in the [SPMiner repo](https://ami-gitlab-01.bbn.com/graph-pattern-matching-and-mining/neural-subgraph-learning-GNN). 

```
PYTHONPATH=<TEXT_OPEN_PYTHONPATH> \
python3 \
./subgraph_pattern_matching/decode.py \
-i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/lists/modal.serifxml.test \
-l
```
