import json
from random import sample

from graph_builder import ID_DELIMITER


class MatchWrapper():

    def __init__(self, match_node_id_to_pattern_node_id, pattern_id, serif_doc):
        '''
        :param match_node_id_to_pattern_node_id: {'a1362': 'CONCEIVER_NODE', 'a1378': 'EVENT_NODE', 'policymakers_a95': 'CONCEIVER_TOKEN', 'epidemic_a91': 'EVENT_TOKEN', 'said_a96': 'SIP', 'need_a81': 'CCOMP_TOKEN'}
        :param serif_doc:
        '''

        self.serif_doc = serif_doc  # TODO why does this need to be instantiated for the references in self.pattern_node_id_to_serif_theory values to work?
        self.docid = serif_doc.docid
        self.pattern_id = pattern_id

        self.match_node_id_to_pattern_node_id = match_node_id_to_pattern_node_id
        self.pattern_node_id_to_match_node_id = dict(map(reversed, match_node_id_to_pattern_node_id.items()))

        self.pattern_node_id_to_serif_theory = {pattern: self.match_to_serif_theory(match_id, serif_doc)
                                                for pattern, match_id in self.pattern_node_id_to_match_node_id.items()}

    def match_to_serif_theory(self, match_id, serif_doc):

        serif_id = match_id.split(ID_DELIMITER)[-1]
        serif_theory = serif_doc.lookup_id(serif_id)

        return serif_theory

    def __str__(self):
        ret = "\n--------------\n"
        ret += "\n".join(["\t".join([k,v]) for k,v in self.retrieve_matched_sentences().items()]) + "\n"
        ret += json.dumps(self.pattern_node_id_to_match_node_id)
        return ret

    def retrieve_matched_sentences(self):
        '''
        :return: list[serif.theory.sentence.Sentence]
        '''
        sentences = dict()
        for p,t in self.pattern_node_id_to_serif_theory.items():
            if t.sentence is not None:
                sentences[".".join([self.docid, t.sentence.id])] = t.sentence.text
        return sentences


class MatchCorpus():

    def __init__(self, matches):
        '''
        :type matches: list[MatchWrapper]
        '''

        self.matches = matches

    def random_sample(self, pattern_ids, sample_size=10):
        '''
        :param pattern_ids: e.g. {'ccomp', 'relaxed_ccomp'}
        :param sample_size:
        :return:
        '''

        match_pool = [m for m in self.matches if m.pattern_id in pattern_ids]

        if len(match_pool) > sample_size:
            return(sample(match_pool, sample_size))
        else:
            return match_pool