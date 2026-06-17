from typing import List, Dict, Any, Optional
import uuid
from ..models.primitives import SemanticPrimitive
from ..models.intent import IntentNode, IntentEdge, IntentGraph
from ..types import IntentType, EdgeType
from ..config import ConflictConfig

class IntentGraphBuilder:
    """
    Transforms SemanticPrimitives into a structured IntentGraph.
    Implements explicit conflict detection and representation.
    """

    def __init__(self, conflict_config: Optional[ConflictConfig] = None):
        self.conflict_config = conflict_config or ConflictConfig()

    def build_from_primitives(self, primitives: List[SemanticPrimitive]) -> IntentGraph:
        """
        Creates a basic intent graph where each primitive becomes a node.
        In a more advanced implementation, this would involve heuristic or LLM-guided clustering.
        """
        graph = IntentGraph()
        nodes = []

        # 1. Generate Nodes
        # For the prototype, we assume each meaningful concept warrants an intent node.
        # We categorize them based on concept prefixes or metadata if available.
        for prim in primitives:
            node_type = self._infer_intent_type(prim)
            node = IntentNode(
                id=f"node_{prim.id}",
                type=node_type,
                semantic_payload=[prim],
                activation_level=prim.semantic_weight
            )
            graph.add_node(node)
            nodes.append(node)

        # 2. Establish basic causal/temporal edges (sequential by default for now)
        for i in range(len(nodes) - 1):
            edge = IntentEdge(
                source_id=nodes[i].id,
                target_id=nodes[i+1].id,
                relationship_type=EdgeType.TEMPORAL,
                semantic_label="sequenced_intent"
            )
            graph.add_edge(edge)

        # 3. Detect and represent conflicts
        self._detect_conflicts(graph)

        return graph

    def _infer_intent_type(self, primitive: SemanticPrimitive) -> IntentType:
        """Heuristic to map semantic concepts to intent types."""
        concept = primitive.concept.lower()
        if "action" in concept or "goal" in concept:
            return IntentType.GOAL
        if "query" in concept or "?" in concept:
            return IntentType.QUERY
        if "constraint" in concept or "must" in concept or "only" in concept:
            return IntentType.CONSTRAINT
        if "emotion" in concept:
            return IntentType.EMOTION
        return IntentType.CONTEXT

    def _detect_conflicts(self, graph: IntentGraph):
        """
        Explicitly identifies and marks conflicts between nodes.
        Requirement 2.4: Explicitly represent conflicts.
        """
        node_list = list(graph.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                n1 = node_list[i]
                n2 = node_list[j]
                
                # Simple conflict heuristic: opposite semantic concepts
                if self._are_conflicting(n1, n2):
                    conflict_info = {
                        "type": "semantic_opposition",
                        "partner_id": n2.id,
                        "description": f"Conflict between {n1.id} and {n2.id}"
                    }
                    n1.conflict_markers.append(conflict_info)
                    
                    # Mutual marking
                    n2.conflict_markers.append({
                        "type": "semantic_opposition",
                        "partner_id": n1.id,
                        "description": f"Conflict between {n2.id} and {n1.id}"
                    })

    def _are_conflicting(self, n1: IntentNode, n2: IntentNode) -> bool:
        """Determines if two nodes have conflicting semantics."""
        concepts1 = [p.concept for p in n1.semantic_payload]
        concepts2 = [p.concept for p in n2.semantic_payload]
        
        # Comprehensive opposition mapping
        opposites = {
            # Speed opposites
            "attribute_fast": "attribute_slow",
            "action_move_fast": "action_move_slow",
            # Size opposites
            "attribute_large": "attribute_small",
            "attribute_big": "attribute_small",
            "attribute_tall": "attribute_short",
            # Temperature opposites
            "attribute_hot": "attribute_cold",
            "attribute_warm": "attribute_cool",
            # Quantity opposites
            "attribute_many": "attribute_few",
            "attribute_much": "attribute_little",
            "attribute_more": "attribute_less",
            # Quality opposites
            "attribute_good": "attribute_bad",
            "attribute_better": "attribute_worse",
            "attribute_best": "attribute_worst",
            # State opposites
            "attribute_on": "attribute_off",
            "attribute_open": "attribute_closed",
            "attribute_start": "attribute_stop",
            "attribute_begin": "attribute_end",
            # Direction opposites
            "attribute_up": "attribute_down",
            "attribute_high": "attribute_low",
            "attribute_top": "attribute_bottom",
            # Logic opposites
            "attribute_true": "attribute_false",
            "attribute_yes": "attribute_no",
            "attribute_always": "attribute_never",
            # Action opposites
            "action_create": "action_destroy",
            "action_add": "action_remove",
            "action_push": "action_pull",
            "action_go": "action_stay",
            "action_move": "action_stop",
            # Energy opposites
            "attribute_strong": "attribute_weak",
            "attribute_hard": "attribute_soft",
            "attribute_heavy": "attribute_light",
            # Cost opposites
            "attribute_expensive": "attribute_cheap",
            "attribute_cost_high": "attribute_cost_low",
        }
        
        for c1 in concepts1:
            for c2 in concepts2:
                if opposites.get(c1) == c2 or opposites.get(c2) == c1:
                    return True
        
        # Additional heuristic: detect same-prefix conflicts (e.g., action_move_fast vs action_move_slow)
        for c1 in concepts1:
            for c2 in concepts2:
                if c1.startswith("action_") and c2.startswith("action_"):
                    if c1 != c2 and ("fast" in c1 and "slow" in c2 or "slow" in c1 and "fast" in c2):
                        return True
                    if c1 != c2 and ("up" in c1 and "down" in c2 or "down" in c1 and "up" in c2):
                        return True
        
        return False
