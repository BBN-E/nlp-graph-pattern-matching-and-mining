import json

def load_propbank_to_xpo_mapping(xpo_overlay_json="/nfs/raid66/u15/aida/releases/entity_linking_files/xpo_v4.1_draft.json"):

    with open(xpo_overlay_json, 'r') as f:
        xpo = json.load(f)

    propbank_to_xpo = dict()

    for qid, info in xpo['events'].items():
        propbank_frame = info['pb_roleset']
        propbank_to_xpo[propbank_frame] = info

    return propbank_to_xpo