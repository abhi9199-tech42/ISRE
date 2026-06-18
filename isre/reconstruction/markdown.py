"""Markdown document output reconstructor."""

from typing import Dict
from .base import OutputReconstructor
from ..models.reasoning import ReasoningDecision


class MarkdownGenerator(OutputReconstructor):
    """
    Generates Markdown output from semantic decisions.
    Uses template-based or deterministic generation to ensure translation-only behavior.
    """

    @property
    def format_type(self) -> str:
        return "markdown"

    def reconstruct(self, decision: ReasoningDecision) -> str:
        """
        Translates the selected path into a coherent Markdown document.
        """
        lines = []
        
        # Title
        lines.append("# Decision Document\n")
        
        # Summary
        lines.append("## Summary")
        lines.append(f"**Selected Path**: {decision.selected_path.id}")
        lines.append(f"**Confidence**: {decision.confidence:.2f}")
        lines.append(f"**Justification**: {decision.justification}\n")
        
        # Steps
        lines.append("## Reasoning Steps")
        for i, step in enumerate(decision.selected_path.steps, 1):
            lines.append(f"### Step {i}")
            lines.append(f"- **Type**: {step.type.value}")
            lines.append(f"- **Activation Level**: {step.activation_level}")
            
            if step.semantic_payload:
                lines.append("- **Concepts**: ")
                concepts = []
                for prim in step.semantic_payload:
                    concepts.append(f"`{prim.concept}`")
                lines.append(f"  {', '.join(concepts)}")
            
            if step.conflict_markers:
                lines.append("- **Conflicts**: ")
                conflicts = []
                for marker in step.conflict_markers:
                    conflicts.append(f"with `{marker['partner_id']}`")
                lines.append(f"  {', '.join(conflicts)}")
            
            lines.append("")
        
        # Alternative paths
        if decision.alternative_paths:
            lines.append("## Alternative Paths")
            for alt_path in decision.alternative_paths:
                lines.append(f"### Path: {alt_path.id}")
                lines.append(f"- **Score**: {alt_path.intent_satisfaction_score:.2f}")
                lines.append(f"- **Justification**: {alt_path.metadata.get('strategy', 'N/A')}\n")
        
        # Knowledge gaps
        if hasattr(decision, 'knowledge_gaps') and decision.knowledge_gaps:
            lines.append("## Knowledge Gaps")
            for gap in decision.knowledge_gaps:
                lines.append(f"- `{gap}`")
        
        # Metadata
        if decision.convergence_metadata:
            lines.append("## Convergence Information")
            meta = decision.convergence_metadata
            lines.append(f"- **Oscillation Steps**: {meta.get('oscillation_steps', 'N/A')}")
            lines.append(f"- **Convergence Tolerance**: {meta.get('tolerance', 'N/A')}")
        
        return "\n".join(lines)