import unittest
import networkx as nx

import serifxml3
from graph_builder import GraphBuilder

from match_utils.node_match_functions import node_type_match
from match_utils.edge_match_functions import edge_type_match



class GraphBuilderTestCase(unittest.TestCase):
    '''
    "Before Alice gave him a heartwarming smile, Bob thought she didn't like him at all."
    '''


    def setUp(self):

        self.GB = GraphBuilder()
        self.serif_doc = serifxml3.Document("/nfs/raid66/u11/users/brozonoy-ad/mtdp_runs/universal_parse/output.amr/universal_sentence.xml")

        '''
        Before Alice gave him a heartwarming smile, Bob thought she didn't like him at all.
        '''
        self.gold_token_nodes = [

            ('Before',       {'id': 'Before',        'nodeType': 'token', 'text': 'Before',          'upos': 'SCONJ',    'xpos': 'IN',   'indexInDoc': '0_0_0',   'incomingDepRel': 'mark'}),
            ('Alice',        {'id': 'Alice',         'nodeType': 'token', 'text': 'Alice',           'upos': 'PROPN',    'xpos': 'NNP',  'indexInDoc': '0_1_1',   'incomingDepRel': 'nsubj'}),
            ('gave',         {'id': 'gave',          'nodeType': 'token', 'text': 'gave',            'upos': 'VERB',     'xpos': 'VBD',  'indexInDoc': '0_2_2',   'incomingDepRel': 'advcl'}),
            ('him__0',       {'id': 'him__0',        'nodeType': 'token', 'text': 'him',             'upos': 'PRON',     'xpos': 'PRP',  'indexInDoc': '0_3_3',   'incomingDepRel': 'iobj'}),
            ('a',            {'id': 'a',             'nodeType': 'token', 'text': 'a',               'upos': 'DET',      'xpos': 'DT',   'indexInDoc': '0_4_4',   'incomingDepRel': 'det'}),
            ('heartwarming', {'id': 'heartwarming',  'nodeType': 'token', 'text': 'heartwarming',    'upos': 'ADJ',      'xpos': 'JJ',   'indexInDoc': '0_5_5',   'incomingDepRel': 'amod'}),
            ('smile',        {'id': 'smile',         'nodeType': 'token', 'text': 'smile',           'upos': 'NOUN',     'xpos': 'NN',   'indexInDoc': '0_6_6',   'incomingDepRel': 'obj'}),
            (',',            {'id': ',',             'nodeType': 'token', 'text': ':',               'upos': 'PUNCT',    'xpos': ':',    'indexInDoc': '0_7_7',   'incomingDepRel': 'punct'}),
            ('Bob',          {'id': 'Bob',           'nodeType': 'token', 'text': 'Bob',             'upos': 'PROPN',    'xpos': 'NNP',  'indexInDoc': '0_8_8',   'incomingDepRel': 'nsubj'}),
            ('thought',      {'id': 'thought',       'nodeType': 'token', 'text': 'thought',         'upos': 'VERB',     'xpos': 'VBD',  'indexInDoc': '0_9_9',   'incomingDepRel': 'root'}),
            ('she',          {'id': 'she',           'nodeType': 'token', 'text': 'she',             'upos': 'PRON',     'xpos': 'PRP',  'indexInDoc': '0_10_10', 'incomingDepRel': 'nsubj'}),
            ('did',          {'id': 'did',           'nodeType': 'token', 'text': 'did',             'upos': 'AUX',      'xpos': 'VBD',  'indexInDoc': '0_11_11', 'incomingDepRel': 'aux'}),
            ("n't",          {'id': "n't",           'nodeType': 'token', 'text': "n't",             'upos': 'PART',     'xpos': 'RB',   'indexInDoc': '0_12_12', 'incomingDepRel': 'advmod'}),
            ('like',         {'id': 'like',          'nodeType': 'token', 'text': 'like',            'upos': 'VERB',     'xpos': 'VB',   'indexInDoc': '0_13_13', 'incomingDepRel': 'ccomp'}),
            ('him__1',       {'id': 'him__1',        'nodeType': 'token', 'text': 'him',             'upos': 'PRON',     'xpos': 'PRP',  'indexInDoc': '0_14_14', 'incomingDepRel': 'obj'}),
            ('at',           {'id': 'at',            'nodeType': 'token', 'text': 'at',              'upos': 'ADV',      'xpos': 'RB',   'indexInDoc': '0_15_15', 'incomingDepRel': 'case'}),
            ('all',          {'id': 'all',           'nodeType': 'token', 'text': 'all',             'upos': 'ADV',      'xpos': 'RB',   'indexInDoc': '0_16_16', 'incomingDepRel': 'obl'}),
            ('.',            {'id': '.',             'nodeType': 'token', 'text': '.',               'upos': 'PUNCT',    'xpos': '.',    'indexInDoc': '0_17_17', 'incomingDepRel': 'punct'})

        ]

        self.gold_dependency_edges = [

            ('gave', 'Before',          {'label': 'mark',   'depRel': 'mark',   'edgeType': 'syntax'}),
            ('gave', 'Alice',           {'label': 'nsubj',  'depRel': 'nsubj',  'edgeType': 'syntax'}),
            ('gave', 'him__0',          {'label': 'iobj',   'depRel': 'iobj',   'edgeType': 'syntax'}),
            ('gave', 'smile',           {'label': 'obj',    'depRel': 'obj',    'edgeType': 'syntax'}),
            ('smile', 'a',              {'label': 'det',    'depRel': 'det',    'edgeType': 'syntax'}),
            ('smile', 'heartwarming',   {'label': 'amod',   'depRel': 'amod',   'edgeType': 'syntax'}),
            ('thought', 'gave',         {'label': 'advcl',  'depRel': 'advcl',  'edgeType': 'syntax'}),
            ('thought', ',',            {'label': 'punct',  'depRel': 'punct',  'edgeType': 'syntax'}),
            ('thought', 'Bob',          {'label': 'nsubj',  'depRel': 'nsubj',  'edgeType': 'syntax'}),
            ('thought', 'like',         {'label': 'ccomp',  'depRel': 'ccomp',  'edgeType': 'syntax'}),
            ('thought', '.',            {'label': 'punct',  'depRel': 'punct',  'edgeType': 'syntax'}),
            ('like', 'she',             {'label': 'nsubj',  'depRel': 'nsubj',  'edgeType': 'syntax'}),
            ('like', 'did',             {'label': 'aux',    'depRel': 'aux',    'edgeType': 'syntax'}),
            ('like', "n't",             {'label': 'advmod', 'depRel': 'advmod', 'edgeType': 'syntax'}),
            ('like', 'him__1',          {'label': 'obj',    'depRel': 'obj',    'edgeType': 'syntax'}),
            ('like', 'all',             {'label': 'obl',    'depRel': 'obl',    'edgeType': 'syntax'}),
            ('all', 'at',               {'label': 'case',   'depRel': 'case',   'edgeType': 'syntax'})

        ]

        self.gold_token_nx_graph = nx.DiGraph()
        self.gold_token_nx_graph.add_nodes_from(self.gold_token_nodes)

        self.gold_syntax_nx_graph = nx.DiGraph()
        self.gold_syntax_nx_graph.add_nodes_from(self.gold_token_nodes)
        self.gold_syntax_nx_graph.add_edges_from(self.gold_dependency_edges)


        '''
        (t / think-01~e.9 
            :arg0 (p / person :name (n / name :op1 "bob")) 
            :arg1 (d / dislike-01~e.4
                        :arg0 (p2 / person :name (n2 / name :op1 "alice"))
                        :arg1 p
                        :degree~e.13 (a / at-all~e.15,16)) 
            :time (b / before :op1 (s / smile-01~e.6
                                        :arg0 p2
                                        :arg2 p
                                        :arg0-of (w / warm-01
                                                    :arg1 (h / heart~e.5)))))
        '''
        self.gold_amr_nodes = [

            ('t__think-01',         {'id': 't__think-01',       'nodeType': 'amr', 'varname': 't',          'content': 'think-01'}),
            ('p__person',           {'id': 'p__person',         'nodeType': 'amr', 'varname': 'p',          'content': 'person'}),
            ('d__dislike-01',       {'id': 'd__dislike-01',     'nodeType': 'amr', 'varname': 'd',          'content': 'dislike-01'}),
            ('b__before',           {'id': 'b__before',         'nodeType': 'amr', 'varname': 'b',          'content': 'before'}),
            ('n__name',             {'id': 'n__name',           'nodeType': 'amr', 'varname': 'n',          'content': 'name'}),
            ('p2__person',          {'id': 'p2__person',        'nodeType': 'amr', 'varname': 'p2',         'content': 'person'}),
            ('a__at-all',           {'id': 'a__at-all',         'nodeType': 'amr', 'varname': 'a',          'content': 'at-all'}),
            ('s__smile-01',         {'id': 's__smile-01',       'nodeType': 'amr', 'varname': 's',          'content': 'smile-01'}),
            ('n|:op1__"bob"',       {'id': 'n|:op1__"bob"',     'nodeType': 'amr', 'varname': 'n|:op1',     'content': '"bob"'}),
            ('n2__name',            {'id': 'n2__name_',         'nodeType': 'amr', 'varname': 'n2',         'content': 'name'}),
            ('n2|:op1__"alice"',    {'id': 'n2|:op1__"alice"',  'nodeType': 'amr', 'varname': 'n2|:op1',    'content': '"alice"'}),

            ('thought', {}),
            ('a', {}),
            ('at', {}),
            ('all', {}),
            ('smile', {}),

        ]

        self.gold_amr_edges = [

            ('t__think-01', 'p__person',        {'label': ':arg0',      'amrRelation': ':arg0',     'edgeType': 'amr'}),
            ('t__think-01', 'd__dislike-01',    {'label': ':arg1',      'amrRelation': ':arg1',     'edgeType': 'amr'}),
            ('t__think-01', 'b__before',        {'label': ':time',      'amrRelation': ':time',     'edgeType': 'amr'}),
            ('p__person', 'n__name',            {'label': ':name',      'amrRelation': ':name',     'edgeType': 'amr'}),
            ('d__dislike-01', 'p2__person',     {'label': ':arg0',      'amrRelation': ':arg0',     'edgeType': 'amr'}),
            ('d__dislike-01', 'a__at-all',      {'label': ':degree',    'amrRelation': ':degree',   'edgeType': 'amr'}),
            ('b__before', 's__smile-01',        {'label': ':op1',       'amrRelation': ':op1',      'edgeType': 'amr'}),
            ('n__name', 'n|:op1__"bob"',        {'label': ':op1',       'amrRelation': ':op1',      'edgeType': 'amr'}),
            ('p2__person', 'n2__name',          {'label': ':name',      'amrRelation': ':name',     'edgeType': 'amr'}),
            ('n2__name', 'n2|:op1__"alice"',    {'label': ':op1',       'amrRelation': ':op1',      'edgeType': 'amr'}),

            ('t__think-01', 'thought',          {'label': 'amrAlignedToken', 'edgeType': 'amrAlignedToken'}),
            ('d__dislike-01', 'a',              {'label': 'amrAlignedToken', 'edgeType': 'amrAlignedToken'}),  # ???
            ('a__at-all', 'at',                 {'label': 'amrAlignedToken', 'edgeType': 'amrAlignedToken'}),
            ('a__at-all', 'all',                {'label': 'amrAlignedToken', 'edgeType': 'amrAlignedToken'}),
            ('s__smile-01', 'smile',            {'label': 'amrAlignedToken', 'edgeType': 'amrAlignedToken'})

        ]

        self.gold_amr_nx_graph = nx.DiGraph()
        self.gold_amr_nx_graph.add_nodes_from(self.gold_amr_nodes)
        self.gold_amr_nx_graph.add_edges_from(self.gold_amr_edges)


        '''
        [
            ((-3, -3, -3), 'Conceiver', (-1, -1, -1), 'Depend-on'),
            ((0, 2, 2), 'Event', (-3, -3, -3), 'pos'),
            ((0, 9, 9), 'Event', (-3, -3, -3), 'pos'),
            ((0, 13, 13), 'Event', (-3, -3, -3), 'neg')
        ]
        '''
        self.gold_modal_nodes = [

            ('a63', {'id': 'a63', 'nodeType': 'modal', 'specialName': 'ROOT_NODE',   'modalNodeType': 'ROOT'}),
            ('a65', {'id': 'a65', 'nodeType': 'modal', 'specialName': 'AUTHOR_NODE', 'modalNodeType': 'Conceiver',  'modalRelation': 'Depend-on'}),
            ('a71', {'id': 'a71', 'nodeType': 'modal', 'specialName': 'Null',        'modalNodeType': 'Event',      'modalRelation': 'pos'}),
            ('a75', {'id': 'a75', 'nodeType': 'modal', 'specialName': 'Null',        'modalNodeType': 'Event',      'modalRelation': 'pos'}),
            ('a79', {'id': 'a79', 'nodeType': 'modal', 'specialName': 'Null',        'modalNodeType': 'Event',      'modalRelation': 'neg'}),

            ('gave', {}),
            ('thought', {}),
            ('like', {})

        ]

        self.gold_modal_edges = [

            ('a63', 'a65', {'label': 'Depend-on',   'modalRelation': 'Depend-on',   'edgeType': 'modal'}),
            ('a65', 'a71', {'label': 'pos',         'modalRelation': 'pos',         'edgeType': 'modal'}),
            ('a65', 'a75', {'label': 'pos',         'modalRelation': 'pos',         'edgeType': 'modal'}),
            ('a65', 'a79', {'label': 'neg',         'modalRelation': 'neg',         'edgeType': 'modal'}),

            ('a71', 'gave',    {'label': 'modalConstituentToken', 'edgeType': 'modalConstituentToken'}),
            ('a75', 'thought', {'label': 'modalConstituentToken', 'edgeType': 'modalConstituentToken'}),
            ('a79', 'like',    {'label': 'modalConstituentToken', 'edgeType': 'modalConstituentToken'})

        ]

        self.gold_modal_nx_graph = nx.DiGraph()
        self.gold_modal_nx_graph.add_nodes_from(self.gold_modal_nodes)
        self.gold_modal_nx_graph.add_edges_from(self.gold_modal_edges)


        '''
        [
            ((-7, -7, -7), 'Timex', (-1, -1, -1), 'Depend-on'), 
            ((0, 2, 2), 'Event', (-7, -7, -7), 'before')
        ]
        '''
        self.gold_temporal_nodes = [

            ('a81', {'id': 'a81', 'nodeType': 'temporal', 'specialName': 'ROOT_NODE',   'temporalNodeType': 'ROOT'}),
            ('a83', {'id': 'a83', 'nodeType': 'temporal', 'specialName': 'DCT_NODE',    'temporalNodeType': 'Timex', 'temporalRelation': 'Depend-on'}),
            ('a87', {'id': 'a87', 'nodeType': 'temporal', 'specialName': 'Null',        'temporalNodeType': 'Event', 'temporalRelation': 'before'}),

            ('gave', {})

        ]

        self.gold_temporal_edges = [

            ('a81', 'a83', {'label': 'Depend-on', 'temporalRelation': 'Depend-on', 'edgeType': 'temporal'}),
            ('a83', 'a87', {'label': 'before',    'temporalRelation': 'before',    'edgeType': 'temporal'}),

            ('a87', 'gave', {'label': ' temporalConstituentToken', 'edgeType': ' temporalConstituentToken'})

        ]

        self.gold_temporal_nx_graph = nx.DiGraph()
        self.gold_temporal_nx_graph.add_nodes_from(self.gold_temporal_nodes)
        self.gold_temporal_nx_graph.add_edges_from(self.gold_temporal_edges)


        self.gold_G = nx.algorithms.operators.compose_all(
            [self.gold_token_nx_graph] + \
            [self.gold_modal_nx_graph] + \
            [self.gold_temporal_nx_graph] + \
            [self.gold_syntax_nx_graph] + \
            [self.gold_amr_nx_graph]
        )


    def test_dependency_parse_build(self):

        assert nx.algorithms.isomorphism.is_isomorphic(self.gold_syntax_nx_graph,
                                                       self.GB.syntactic_dependency_parse_to_networkx(self.serif_doc.sentences[0]),
                                                       node_match=None,  # node_type_match
                                                       edge_match=None)  # edge_type_match


    def test_amr_build(self):
        
        assert nx.algorithms.isomorphism.is_isomorphic(self.gold_amr_nx_graph,
                                                       self.GB.amr_parse_to_networkx(self.serif_doc.sentences[0]),
                                                       node_match=None,
                                                       edge_match=None)


    def test_modal_dependency_parse_build(self):

        assert nx.algorithms.isomorphism.is_isomorphic(self.gold_modal_nx_graph,
                                                       self.GB.modal_dependency_parse_to_networkx(self.serif_doc),
                                                       node_match=None,
                                                       edge_match=None)


    def test_temporal_dependency_parse_build(self):

        assert nx.algorithms.isomorphism.is_isomorphic(self.gold_temporal_nx_graph,
                                                       self.GB.temporal_dependency_parse_to_networkx(self.serif_doc),
                                                       node_match=None,
                                                       edge_match=None)


    def test_composition_does_not_lose_information(self):
        '''
        AMR, modal/temporal dependencies don't store token features in aligned token nodes.
        Composition must ensure that empty token nodes get populated with features from full token nodes.
        '''

        assert self.gold_amr_nx_graph.nodes['thought'] == {}

        assert nx.algorithms.operators.compose(self.gold_amr_nx_graph,
                                               self.gold_token_nx_graph).nodes['thought'] == {'id': 'thought',
                                                                                              'nodeType': 'token',
                                                                                              'text': 'thought',
                                                                                              'upos': 'VERB',
                                                                                              'xpos': 'VBD',
                                                                                              'indexInDoc': '0_9_9',
                                                                                              'incomingDepRel': 'root'}


    def test_composed_graph_build(self):

        assert nx.algorithms.isomorphism.is_isomorphic(self.gold_G,
                                                       self.GB.serif_doc_to_networkx(self.serif_doc),
                                                       node_match=None,
                                                       edge_match=None)



class SubgraphIsomorphismTestCase(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main()