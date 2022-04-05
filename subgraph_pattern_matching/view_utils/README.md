# view-graphs

Visualize networkx graphs representing various NLP parses from a serifxml document

Requires `networkx` to be installed in the Python environment.  Requires PYTHONPATH include `text-open` and `subgraph-pattern-matching/subgraph_pattern_matching`.

```
SGPM=/home/dzajic/dev/projects/rozonoyer/subgraph-pattern-matching/subgraph_pattern_matching
TEXTOPEN=/nfs/raid91/u10/developers/dzajic-ad/projects/text-group/text-open/src/python
PYTHONPATH=$TEXTOPEN:$SGPM python --help

usage: view_graphs.py [-h] -i INPUT [-l] -w WORKSPACE

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
  -l, --list            input is list of serifxmls rather than serifxml path
  -w WORKSPACE, --workspace WORKSPACE
```

To view these beauties from a browser, start a python server in the workspace directory.
```
SOME_AVAILABLE_PORT=8085
python -m http.server $SOME_AVAILABLE_PORT
```
You can view the graphs in a browser using the hostname of the machine where the server runs and the relative path of the html file.
```
http://dg712.bbn.com:8085/html.foxnews_71348028/amr_tok_04_graph.html
```
