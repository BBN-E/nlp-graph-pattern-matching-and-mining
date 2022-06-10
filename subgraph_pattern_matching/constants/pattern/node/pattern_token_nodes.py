from .pattern_nodes import PatternNodes

from constants.pattern.id.pattern_token_node_ids import PatternTokenNodeIDs
from constants.common.attrs.node.node_attrs import NodeAttrs
from constants.common.attrs.node.token_node_attrs import TokenNodeAttrs
from constants.common.types.node_types import NodeTypes

from constants.special_symbols import DISJUNCTION


class PatternTokenNodes(PatternNodes):

    SIP_TOKEN_NODE = (PatternTokenNodeIDs.SIP_TOKEN_NODE_ID,
                      {NodeAttrs.node_type: NodeTypes.token, TokenNodeAttrs.upos: 'VERB'})

    CONCEIVER_TOKEN_NODE = (PatternTokenNodeIDs.CONCEIVER_TOKEN_NODE_ID,
                            {NodeAttrs.node_type: NodeTypes.token})

    EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})

    ROOT_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                             {NodeAttrs.node_type: NodeTypes.token,
                              TokenNodeAttrs.upos: DISJUNCTION.join(['VERB', 'ADJ']),
                              TokenNodeAttrs.incoming_dep_rel: 'root'})

    ROOT_VERB_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                    {NodeAttrs.node_type: NodeTypes.token,
                                     TokenNodeAttrs.upos: 'VERB',
                                     TokenNodeAttrs.incoming_dep_rel: 'root'})

    ROOT_ADJ_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                 {NodeAttrs.node_type: NodeTypes.token,
                                  TokenNodeAttrs.upos: 'ADJ',
                                  TokenNodeAttrs.incoming_dep_rel: 'root'})

    CCOMP_VERB_EVENT_TOKEN_NODE = (PatternTokenNodeIDs.EVENT_TOKEN_NODE_ID,
                                   {NodeAttrs.node_type: NodeTypes.token,
                                    TokenNodeAttrs.upos: 'VERB',
                                    TokenNodeAttrs.incoming_dep_rel: 'ccomp'})

    CCOMP_TOKEN_NODE = (PatternTokenNodeIDs.CCOMP_TOKEN_NODE_ID,
                        {NodeAttrs.node_type: NodeTypes.token})  # may be same as event token
