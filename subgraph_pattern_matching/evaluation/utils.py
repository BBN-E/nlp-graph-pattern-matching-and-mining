from enum import Enum
from collections import defaultdict

import serifxml3
from serif.theory.token import Token


class AnnotationScheme(Enum):

    IDENTIFICATION = 1
    CLASSIFICATION = 2
    IDENTIFICATION_CLASSIFICATION = 3


class KnowledgeElement(Enum):

    NAMED_ENTITY = 1
    EVENT_TRIGGER = 2
    EVENT_ARGUMENT = 3


def create_corpus_directory(corpus_paths_dict):
    '''

    :param corpus_paths_dict: {'TRAIN': path(s), 'DEV': path(s), 'TEST': path(s)}
    :return:

        {
            'TRAIN':
                {
                    serif_doc_1.id: serif_doc_1,
                    ...
                    serif_doc_k.id: serif_doc_k
                },
            'DEV': ...
            'TEST': ...
        }

    '''

    corpus_dir = defaultdict(lambda: defaultdict())

    for SPLIT in ['TRAIN', 'DEV', 'TEST']:

        if corpus_paths_dict[SPLIT].endswith('.xml'):

            serif_doc = serifxml3.Document(corpus_paths_dict[SPLIT])
            corpus_dir[SPLIT][serif_doc.docid] = serif_doc

        else:  # assume list of serifxml paths

            with open(corpus_paths_dict[SPLIT], 'r') as f:

                split_serifxml_paths = [l.strip() for l in f.readlines()]
                for serifxml_path in split_serifxml_paths:

                    serif_doc = serifxml3.Document(serifxml_path)
                    corpus_dir[SPLIT][serif_doc.id] = serif_doc

    return corpus_dir


def serif_sentence_to_ner_bio_list(serif_sentence, annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):
    '''

    :param serif_sentence: serif.theory.sentence.Sentence
    :param annotation_scheme: TODO: identification, identification-classification, BIO, IO
    :return: list[str]
    '''

    bio_list = ['O'] * len(serif_sentence.token_sequence)

    if serif_sentence.mention_set:
        for mention in serif_sentence.mention_set:

            mention_bio = []
            if mention.tokens:
                for i in range(len(mention.tokens)):
                    # if i == 0:
                    #     if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                    #         mention_bio.append(f'B-{mention.entity_type}')
                    #     else:  # 'identification'
                    #         mention_bio.append('B')
                    # else:
                    if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                        mention_bio.append(f'I-{mention.entity_type}')
                    else:  # identification
                        mention_bio.append('I')

            mention_token_indices = [t.index() for t in mention.tokens]
            for i, j in enumerate(mention_token_indices):
                bio_list[j] = mention_bio[i]

    return bio_list


def serif_sentence_to_event_trigger_bio_list(serif_sentence, annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):
    '''

    :param serif_sentence: serif.theory.sentence.Sentence
    :param annotation_scheme: TODO: identification, identification-classification, BIO, IO
    :return: list[str]
    '''

    bio_list = ['O'] * len(serif_sentence.token_sequence)

    if serif_sentence.event_mention_set:
        for event_mention in serif_sentence.event_mention_set:

            event_mention_bio = []
            if event_mention.tokens:
                for i in range(len(event_mention.tokens)):
                    if i == 0:
                        if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                            event_mention_bio.append(f'B-{event_mention.event_type}')
                        else:  # 'identification'
                            event_mention_bio.append('B')
                    else:
                        if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                            event_mention_bio.append(f'I-{event_mention.event_type}')
                        else:  # identification
                            event_mention_bio.append('I')

            event_mention_token_indices = [t.index() for t in event_mention.tokens]
            for i, j in enumerate(event_mention_token_indices):
                bio_list[j] = event_mention_bio[i]

    return bio_list


def serif_sentence_to_event_argument_bio_list(serif_sentence, annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION):
    '''

    :param serif_sentence: serif.theory.sentence.Sentence
    :param annotation_scheme: TODO: identification, identification-classification, BIO, IO
    :return: list[str]
    '''

    bio_list = ['O'] * len(serif_sentence.token_sequence)

    if serif_sentence.event_mention_set:
        for event_mention in serif_sentence.event_mention_set:

            event_argument_bio = []
            if event_mention.arguments:
                for event_argument in event_mention.arguments:
                    if event_argument.value.tokens:

                        for i in range(len(event_argument.value.tokens)):
                            if i == 0:
                                if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                                    event_argument_bio.append(f'B-{event_argument.role}')
                                else:  # 'identification'
                                    event_argument_bio.append('B')
                            else:
                                if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION:
                                    event_argument_bio.append(f'I-{event_argument.role}')
                                else:  # identification
                                    event_argument_bio.append('I')

            event_argument_token_indices = [t.index() for t in event_mention.tokens]
            for i, j in enumerate(event_argument_token_indices):
                bio_list[j] = event_argument_bio[i]

    return bio_list


def serif_sentence_to_bio_list_based_on_predictions(
        serif_sentence,
        matches_for_sentence,
        ke=KnowledgeElement.NAMED_ENTITY,
        annotation_scheme=AnnotationScheme.IDENTIFICATION_CLASSIFICATION
):
    '''

    :param serif_sentence: serif.theory.sentence.Sentence
    :param matches_for_sentence: list[match_wrapper.MatchWrapper]
    :param ke:
    :param annotation_scheme:
    :return:
    '''

    bio_list = ['O'] * len(serif_sentence.token_sequence)

    if matches_for_sentence:

        for match in matches_for_sentence:

            if match.serif_sentence is not None:

                # collect all tokens from match
                serif_tokens_for_match = []
                for match_node_id, pattern_node_id in match.match_node_id_to_pattern_node_id.items():

                    # only match tokens that were part of the annotation in the pattern

                    if ke == KnowledgeElement.NAMED_ENTITY:
                        ke_node_ids = match.pattern.get_named_entity_node_ids()
                    elif ke == KnowledgeElement.EVENT_TRIGGER:
                        ke_node_ids = match.pattern.get_event_trigger_node_ids()
                    elif ke == KnowledgeElement.EVENT_ARGUMENT:
                        ke_node_ids = match.pattern.get_event_argument_node_ids()
                    else: raise NotImplementedError

                    if ke_node_ids:
                        if pattern_node_id not in ke_node_ids:
                            continue

                    serif_theory = match.match_to_serif_theory(match_id=match_node_id, serif_doc=match.serif_doc)
                    if serif_theory is not None:

                        # match is serif Token
                        if type(serif_theory) == Token:
                            serif_tokens_for_match.append(serif_theory)

                if len(serif_tokens_for_match) > 0:

                    contiguous_token_chunks = chunk_up_list_of_tokens_into_lists_of_contiguous_tokens(
                        serif_tokens_for_match)
                    for chunk in contiguous_token_chunks:
                        for i, token in enumerate(chunk):
                            # if i == 0:
                            #     bio_list[token.index()] = f"B-{match.category}" if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION else "B"
                            # else:
                            bio_list[
                                token.index()] = f"I-{match.category}" if annotation_scheme == AnnotationScheme.IDENTIFICATION_CLASSIFICATION else "I"

    return bio_list


def chunk_up_list_of_tokens_into_lists_of_contiguous_tokens(serif_tokens):
    '''

    tokens with indices [1,2,4,5,6,8,9] -> [[1,2],[4,5,6],[8,9]]

    :param serif_tokens: list[serif.theory.token.Token]
    :return: list[list[serif.theory.token.Token]]
    '''

    serif_tokens = sorted(serif_tokens, key=lambda t: t.index())
    contiguous_tokens = []

    chunk = [serif_tokens[0]]
    for i, token in enumerate(serif_tokens[1:]):

        if serif_tokens[i + 1].index() == serif_tokens[i].index() + 1:
            chunk.append(serif_tokens[i + 1])

        else:
            contiguous_tokens.append(chunk)
            chunk = [serif_tokens[i + 1]]

    contiguous_tokens.append(chunk)

    return contiguous_tokens


if __name__ == '__main__':
    d = serifxml3.Document("/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/eng.testa.xml")
    for s in d.sentences[:10]:
        print([t.text for t in s.token_sequence])
        print(serif_sentence_to_ner_bio_list(serif_sentence=s))