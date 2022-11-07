from subgraph_pattern_matching.constants.common.attrs.node.modal_node_attrs import ModalNodeAttrs
from subgraph_pattern_matching.constants.common.attrs.node.node_attrs import NodeAttrs
from subgraph_pattern_matching.constants.common.types.node_types import NodeTypes
from subgraph_pattern_matching.constants.pattern.id.pattern_modal_node_ids import PatternModalNodeIDs

from .pattern_nodes import PatternNodes


class PatternModalNodes(PatternNodes):

    CONCEIVER_NODE = (PatternModalNodeIDs.CONCEIVER_NODE_ID,
                      {NodeAttrs.node_type: NodeTypes.modal, ModalNodeAttrs.modal_node_type: 'Conceiver'})

    EVENT_NODE = (PatternModalNodeIDs.EVENT_NODE_ID,
                  {NodeAttrs.node_type: NodeTypes.modal, ModalNodeAttrs.modal_node_type: 'Event'})

    AUTHOR_CONCEIVER_NODE = (PatternModalNodeIDs.AUTHOR_CONCEIVER_NODE_ID,
                             {NodeAttrs.node_type: NodeTypes.modal,
                              ModalNodeAttrs.modal_node_type: 'Conceiver',
                              ModalNodeAttrs.special_name: 'AUTHOR_NODE'})
