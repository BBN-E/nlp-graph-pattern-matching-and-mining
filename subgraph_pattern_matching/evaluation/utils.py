from collections import defaultdict

import serifxml3


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

    corpus_dir = defaultdict()

    for SPLIT in ['TRAIN', 'DEV', 'TEST']:

        if corpus_paths_dict[SPLIT].endswith('.xml'):

            serif_doc = serifxml3.Document(corpus_paths_dict[SPLIT])
            corpus_dir[SPLIT][serif_doc.id] = serif_doc

        else:  # assume list of serifxml paths

            with open(corpus_paths_dict[SPLIT], 'r') as f:

                split_serifxml_paths = [l.strip() for l in f.readlines()]
                for serifxml_path in split_serifxml_paths:

                    serif_doc = serifxml3.Document(serifxml_path)
                    corpus_dir[SPLIT][serif_doc.id] = serif_doc

    return corpus_dir


def serif_sentence_to_ner_bio_list(serif_sentence, annotation_scheme=None):
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
                    if i == 0:
                        mention_bio.append(f'B-{mention.entity_type}')
                    else:
                        mention_bio.append(f'I-{mention.entity_type}')

            mention_token_indices = [t.index() for t in mention.tokens]
            for i, j in enumerate(mention_token_indices):
                bio_list[j] = mention_bio[i]

    return bio_list


if __name__ == '__main__':
    d = serifxml3.Document("/nfs/raid90/u10/users/brozonoy-ad/data/conll/serifxml/eng.testa.xml")
    for s in d.sentences[:10]:
        print([t.text for t in s.token_sequence])
        print(serif_sentence_to_ner_bio_list(serif_sentence=s))