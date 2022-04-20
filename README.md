# subgraph-pattern-matching

Using subgraph pattern matching over compositions of multifarious linguistic parses to extract meaningful knowledge elements. 

Requires `networkx` and `penman` (for matching over AMR graphs) to be installed in the environment.

```
PYTHONPATH=<TEXT_OPEN_PYTHONPATH> \
python3 \
./subgraph_pattern_matching/decode.py \
-i /nfs/raid66/u11/users/brozonoy-ad/modal_and_temporal_parsing/mtdp_data/lists/modal.serifxml.test \
-l
```
