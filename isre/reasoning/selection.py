"""Competitive path selection with oscillatory modulation."""

from typing import List
from ..models.reasoning import ReasoningPath, ReasoningDecision
from ..models.intent import IntentNode
from ..types import IntentType
from .dynamics import OscillatoryGate
from ..config import ReasoningConfig

class CompetitiveSelector:
    """
    Evaluates and selects the best reasoning path based on multiple objectives.
    Uses oscillatory dynamics for temporal path modulation.
    Requirement 3.2: Competitive selection.
    Requirement 3.3: Oscillatory gating mechanisms.
    """

    def __init__(self, reasoning_config: ReasoningConfig = None):
        self.config = reasoning_config or ReasoningConfig()
        self.max_oscillation_steps = self.config.max_oscillation_steps
        self.tolerance = self.config.oscillation_tolerance

    def select(self, paths: List[ReasoningPath]) -> ReasoningDecision:
        if not paths:
            raise ValueError("Cannot select from empty path list")

        # 1. Calculate base scores for each path
        base_scores = []
        for path in paths:
            satisfaction = self._score_intent_satisfaction(path)
            compliance = self._score_constraint_compliance(path)
            coherence = self._score_semantic_coherence(path)

            path.intent_satisfaction_score = satisfaction
            path.constraint_compliance_score = compliance
            path.semantic_coherence_score = coherence

            base_score = (satisfaction * self.config.intent_satisfaction_weight) + \
                        (compliance * self.config.constraint_compliance_weight) + \
                        (coherence * self.config.semantic_coherence_weight)
            base_scores.append(base_score)

        # 2. Apply oscillatory modulation for temporal dynamics
        final_scores = self._apply_oscillatory_modulation(base_scores)

        # 3. Select the best path
        best_idx = max(range(len(paths)), key=lambda i: final_scores[i])
        best_path = paths[best_idx]
        best_score = final_scores[best_idx]

        return ReasoningDecision(
            selected_path=best_path,
            justification=f"Selected path with highest oscillatory score: {best_score:.2f} "
                          f"(Sat: {best_path.intent_satisfaction_score:.2f}, "
                          f"Comp: {best_path.constraint_compliance_score:.2f}, "
                          f"Coh: {best_path.semantic_coherence_score:.2f})",
            confidence=best_score,
            alternative_paths=[p for i, p in enumerate(paths) if i != best_idx],
            convergence_metadata={
                "base_scores": base_scores,
                "final_scores": final_scores,
                "oscillation_steps": self.max_oscillation_steps
            }
        )

    def _apply_oscillatory_modulation(self, base_scores: List[float]) -> List[float]:
        """
        Apply Hopf oscillator dynamics to modulate path scores over time.
        Each path gets an oscillator; activation converges to highlight the best path.
        """
        n_paths = len(base_scores)
        if n_paths == 1:
            return base_scores

        # Initialize one oscillator per path, seeded with base score
        oscillators = []
        for score in base_scores:
            osc = OscillatoryGate(frequency=self.config.oscillator_frequency,
                                  bifurcation=self.config.oscillator_bifurcation)
            # Seed initial state proportional to base score
            osc.z = complex(0.1 + score * 0.5, 0.1)
            oscillators.append(osc)

        # Run oscillatory dynamics
        prev_activations = [0.0] * n_paths
        for step in range(self.max_oscillation_steps):
            curr_activations = []
            for osc in oscillators:
                osc.step()
                curr_activations.append(osc.activation)

            # Check convergence
            max_delta = max(abs(curr_activations[i] - prev_activations[i])
                           for i in range(n_paths))
            if max_delta < self.tolerance and step > 10:
                break
            prev_activations = curr_activations

        # Final activations modulate base scores
        final_scores = []
        for i, (base, osc) in enumerate(zip(base_scores, oscillators)):
            # Combine base score with oscillatory activation
            modulated = (base * 0.6) + (osc.activation * 0.4)
            final_scores.append(modulated)

        return final_scores

    def _score_intent_satisfaction(self, path: ReasoningPath) -> float:
        """High score if GOAL nodes are present and active."""
        goals = [n for n in path.steps if n.type == IntentType.GOAL]
        if not goals:
            return 0.1
        # Simple heuristic: sum of activation levels of goals / total possible
        return sum(n.activation_level for n in goals) / len(goals)

    def _score_constraint_compliance(self, path: ReasoningPath) -> float:
        """
        High score if CONSTRAINT nodes are respected.
        In our prototype, if a path *removed* a node due to conflict, it might be cleaner.
        Checking if remaining nodes have internal conflicts.
        """
        # Penalize if any active node has a conflict marker pointing to another active node in the path
        active_ids = {n.id for n in path.steps}
        conflicts_found = 0
        
        for node in path.steps:
            for marker in node.conflict_markers:
                if marker['partner_id'] in active_ids:
                    conflicts_found += 1
        
        # If conflicts exist in the path, compliance is low
        if conflicts_found > 0:
            return 0.2
        return 1.0

    def _score_semantic_coherence(self, path: ReasoningPath) -> float:
        """
        Measure of how 'smooth' the semantic transition is between consecutive nodes.
        Considers concept similarity, type consistency, and activation smoothness.
        """
        if len(path.steps) <= 1:
            return 1.0

        scores = []
        for i in range(len(path.steps) - 1):
            node_a = path.steps[i]
            node_b = path.steps[i + 1]

            # 1. Concept similarity (shared concepts = higher score)
            concepts_a = {p.concept for p in node_a.semantic_payload}
            concepts_b = {p.concept for p in node_b.semantic_payload}
            if concepts_a and concepts_b:
                overlap = len(concepts_a & concepts_b)
                total = len(concepts_a | concepts_b)
                concept_sim = overlap / total if total > 0 else 0.0
            else:
                concept_sim = 0.0

            # 2. Type consistency (same type = smoother transition)
            type_match = 1.0 if node_a.type == node_b.type else 0.5

            # 3. Activation smoothness (similar activation = smoother)
            act_diff = abs(node_a.activation_level - node_b.activation_level)
            act_smooth = max(0.0, 1.0 - act_diff)

            # Weighted combination
            pair_score = (concept_sim * 0.4) + (type_match * 0.3) + (act_smooth * 0.3)
            scores.append(pair_score)

        return sum(scores) / len(scores) if scores else 0.5
