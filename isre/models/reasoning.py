"""Reasoning path and decision data models."""

from typing import Any

from pydantic import BaseModel, Field

from .intent import IntentNode


class ReasoningPath(BaseModel):
    """
    A sequence of steps followed by the reasoning engine.
    """
    id: str
    steps: list[IntentNode]
    intent_satisfaction_score: float = 0.0
    constraint_compliance_score: float = 0.0
    semantic_coherence_score: float = 0.0
    oscillation_state: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class ReasoningDecision(BaseModel):
    """
    The final selection from multiple reasoning paths.
    """
    selected_path: ReasoningPath
    justification: str
    confidence: float
    alternative_paths: list[ReasoningPath]
    convergence_metadata: dict[str, Any] = Field(default_factory=dict)
