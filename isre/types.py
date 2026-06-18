"""Core type definitions and enums for the ISRE system."""

from enum import Enum


class IntentType(Enum):
    GOAL = "goal"
    CONTEXT = "context"
    QUERY = "query"
    CONSTRAINT = "constraint"
    EMOTION = "emotion"

class EdgeType(Enum):
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    PRIORITY = "priority"

class SemanticType(Enum):
    CONCEPT = "concept"
    ACTION = "action"
    ATTRIBUTE = "attribute"
    RELATION = "relation"
