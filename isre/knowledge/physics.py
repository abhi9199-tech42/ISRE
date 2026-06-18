"""Physics constraint rule engine for physical possibility validation."""

from typing import Any


class PhysicsRuleEngine:
    """
    Applies physical constraints and laws to reasoning.
    Requirement 4.2: Integrate physics rules.
    """

    def check_physical_possibility(self, action_concept: str, context: dict[str, Any]) -> bool:
        """
        Determines if an action is physically possible in the given context.
        """
        # Simple prototype rules: flying requires wings or aircraft
        return not (action_concept == "fly" and not context.get("has_wings") and not context.get("has_aircraft"))

    def get_constraints(self, concept: str) -> list[str]:
        """Returns physical constraints associated with a concept."""
        constraints = []
        if concept == "object_solid":
            constraints.append("cannot_pass_through_solids")
        return constraints
