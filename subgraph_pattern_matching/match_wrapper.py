import json
from random import sample
from collections import defaultdict

from constants.special_symbols import ID_DELIMITER
from constants.pattern.id.pattern_modal_node_ids import PatternModalNodeIDs


class MatchWrapper():
    '''
    Convenient wrapper to store isomorphism dicts and map matches back to serifxml
    '''

    def __init__(self,
                 match_node_id_to_pattern_node_id,
                 pattern_id,
                 serif_sentence,
                 serif_doc,
                 annotated_node_ids=None,
                 category=None):
        '''
        :param match_node_id_to_pattern_node_id: {'a1362': 'CONCEIVER_NODE', 'a1378': 'EVENT_NODE', 'policymakers_a95': 'CONCEIVER_TOKEN', 'epidemic_a91': 'EVENT_TOKEN', 'said_a96': 'SIP', 'need_a81': 'CCOMP_TOKEN'}
        :param serif_doc:
        '''

        self.serif_doc = serif_doc  # TODO why does this need to be instantiated for the references in self.pattern_node_id_to_serif_theory values to work?
        self.serif_sentence = serif_sentence
        self.docid = serif_doc.docid
        self.pattern_id = pattern_id

        self.match_node_id_to_pattern_node_id = match_node_id_to_pattern_node_id
        self.pattern_node_id_to_match_node_id = dict(map(reversed, match_node_id_to_pattern_node_id.items()))

        self.pattern_node_id_to_serif_theory = {pattern: self.match_to_serif_theory(match_id, serif_doc)
                                                for pattern, match_id in self.pattern_node_id_to_match_node_id.items()}

        self.annotated_node_ids = annotated_node_ids
        self.category = category

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
        :return:
        '''
        sentences = dict()
        for p,t in self.pattern_node_id_to_serif_theory.items():
            if t.sentence is not None:
                sentences[".".join([self.docid, t.sentence.id])] = t.sentence.text
        return sentences


class MatchCorpus():
    '''
    Wraps a collection of MatchWrapper objects, facilitates corpus statistics, and corpus-level conversions
    '''

    def __init__(self, matches):
        '''
        :type matches: list[MatchWrapper]
        '''

        self.matches = matches

    def organize_matches_by_serif_doc_and_serif_sentence(self, per_sentence=False):

        if per_sentence:
            match_dict = defaultdict(lambda: defaultdict(list))
            for m in self.matches:
                assert m.serif_doc is not None
                assert m.serif_sentence is not None
                match_dict[m.serif_doc.docid][m.serif_sentence.id].append(m)
        else:
            match_dict = defaultdict(list)
            for m in self.matches:
                assert m.serif_doc is not None
                match_dict[m.serif_doc.docid].append(m)

        return match_dict

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

    def extraction_stats(self):

        stats = defaultdict(int)
        for m in self.matches:
            stats[m.pattern_id] += 1
        print(json.dumps(stats, indent=4, sort_keys=True))

        return stats

    def count_intersentence_conceiver_event_edges(self):

        n = len([m for m in self.matches if len(m.retrieve_matched_sentences()) > 1])
        print("# inter-sentence conceive-event edges:", n)
        return n

    def to_mtra_pairs(self, include_pattern_id=False):
        '''
        Assumes each match contains 'CONCEIVER_NODE' and 'EVENT_NODE' (claim pattern extractions)

        :return: list[(conceiver_mtra, event_mtra)]
        '''

        conceiver_event_mtras = []

        for i, match in enumerate(self.matches):
            if PatternModalNodeIDs.CONCEIVER_NODE_ID in match.pattern_node_id_to_match_node_id:
                conceiver_mtra = match.match_to_serif_theory(match.pattern_node_id_to_match_node_id[PatternModalNodeIDs.CONCEIVER_NODE_ID], match.serif_doc)
            else:  # must be AUTHOR_CONCEIVER
                conceiver_mtra = match.match_to_serif_theory(match.pattern_node_id_to_match_node_id[PatternModalNodeIDs.AUTHOR_CONCEIVER_NODE_ID], match.serif_doc)
            event_mtra = match.match_to_serif_theory(match.pattern_node_id_to_match_node_id[PatternModalNodeIDs.EVENT_NODE_ID], match.serif_doc)

            if include_pattern_id:
                conceiver_event_mtras.append([conceiver_mtra, event_mtra, match.pattern_id])
            else:
                conceiver_event_mtras.append([conceiver_mtra, event_mtra])

        return conceiver_event_mtras