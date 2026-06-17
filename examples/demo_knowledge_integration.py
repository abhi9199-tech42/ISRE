"""
Demonstration of ISRE's Layer 4: World Knowledge Integration

This script showcases how ISRE dynamically queries external knowledge sources
rather than embedding knowledge in model weights like traditional LLMs.

Key Features:
1. Dynamic Knowledge Querying (not embedded in weights)
2. Physics Rules Integration
3. Domain-Specific Logic Modules
4. Explicit Knowledge Gap Detection
5. Separation of Reasoning and Knowledge
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from isre.knowledge.engine import KnowledgeQueryEngine
from isre.knowledge.physics import PhysicsRuleEngine
from isre.knowledge.gaps import KnowledgeGapDetector
from isre.knowledge.domain import DomainLogicManager, DomainModule
from isre.models.primitives import SemanticPrimitive
from isre.models.intent import IntentNode
from isre.models.reasoning import ReasoningPath, ReasoningDecision
from isre.types import IntentType

def print_section(title: str):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def demo_dynamic_knowledge_query():
    """Demonstrate dynamic external knowledge querying"""
    print_section("1. DYNAMIC KNOWLEDGE QUERYING")
    
    print("Unlike LLMs that embed knowledge in weights, ISRE queries external sources.\n")
    
    # Initialize knowledge engine
    engine = KnowledgeQueryEngine()
    
    # Simulate adding facts to external database
    print("Populating External Knowledge Base:")
    print("-" * 45)
    engine.update_knowledge("apple", {
        "category": "fruit",
        "edible": True,
        "color": ["red", "green"],
        "nutrition": {"vitamin_c": "high"}
    })
    engine.update_knowledge("car", {
        "category": "vehicle",
        "requires": "fuel",
        "max_speed": 200
    })
    print("  ✓ Added 'apple' facts")
    print("  ✓ Added 'car' facts")
    
    # Query knowledge dynamically
    print("\nQuerying Knowledge Dynamically:")
    print("-" * 45)
    
    result = engine.query("apple")
    if result:
        print(f"  Query: 'apple'")
        print(f"  Source: {result.source_id}")
        print(f"  Content: {result.content}")
        print(f"  Confidence: {result.confidence}")
    
    result = engine.query("car")
    if result:
        print(f"\n  Query: 'car'")
        print(f"  Content: {result.content}")
    
    # Query unknown concept
    result = engine.query("unicorn")
    print(f"\n  Query: 'unicorn'")
    print(f"  Result: {result}")
    print("  ✓ Returns None for unknown concepts (no hallucination!)")
    
    print("\n✓ Knowledge is queried dynamically, not embedded in model weights")
    print("✓ Can be updated in real-time without retraining")

def demo_physics_rules():
    """Demonstrate physics rule integration"""
    print_section("2. PHYSICS RULES INTEGRATION")
    
    print("ISRE can integrate external physics engines to validate actions.\n")
    
    physics = PhysicsRuleEngine()
    
    # Test physical possibility
    print("Testing Physical Constraints:")
    print("-" * 45)
    
    # Test 1: Flying without wings
    context1 = {"has_wings": False, "has_aircraft": False}
    possible1 = physics.check_physical_possibility("fly", context1)
    print(f"  Action: 'fly'")
    print(f"  Context: {context1}")
    print(f"  Physically Possible: {possible1}")
    
    # Test 2: Flying with aircraft
    context2 = {"has_wings": False, "has_aircraft": True}
    possible2 = physics.check_physical_possibility("fly", context2)
    print(f"\n  Action: 'fly'")
    print(f"  Context: {context2}")
    print(f"  Physically Possible: {possible2}")
    
    # Get constraints
    print("\n  Constraints for 'object_solid':")
    constraints = physics.get_constraints("object_solid")
    for c in constraints:
        print(f"    - {c}")
    
    print("\n✓ Physics rules are external modules, not learned patterns")
    print("✓ Can be swapped or updated independently of reasoning engine")

def demo_domain_logic():
    """Demonstrate pluggable domain-specific logic"""
    print_section("3. DOMAIN-SPECIFIC LOGIC MODULES")
    
    print("ISRE supports pluggable domain modules for specialized reasoning.\n")
    
    # Create a simple medical domain module
    class MedicalDomainModule:
        def execute(self, inputs):
            symptom = inputs.get("symptom", "")
            
            # Simple medical logic (in reality, this would query medical databases)
            if symptom == "fever":
                return {
                    "possible_causes": ["infection", "inflammation"],
                    "recommended_action": "consult_doctor",
                    "urgency": "medium"
                }
            return {"status": "unknown_symptom"}
    
    # Create a financial domain module
    class FinancialDomainModule:
        def execute(self, inputs):
            amount = inputs.get("amount", 0)
            risk_tolerance = inputs.get("risk_tolerance", "medium")
            
            if amount < 1000:
                return {"recommendation": "savings_account", "risk": "low"}
            elif risk_tolerance == "high":
                return {"recommendation": "stocks", "risk": "high"}
            else:
                return {"recommendation": "bonds", "risk": "medium"}
    
    # Register modules
    manager = DomainLogicManager()
    manager.register_module("medical", MedicalDomainModule())
    manager.register_module("financial", FinancialDomainModule())
    
    print("Registered Domain Modules:")
    print("-" * 45)
    print("  ✓ Medical Domain")
    print("  ✓ Financial Domain")
    
    # Execute domain logic
    print("\nExecuting Medical Domain Logic:")
    print("-" * 45)
    medical_result = manager.execute_logic("medical", {"symptom": "fever"})
    print(f"  Input: symptom='fever'")
    print(f"  Output: {medical_result}")
    
    print("\nExecuting Financial Domain Logic:")
    print("-" * 45)
    financial_result = manager.execute_logic("financial", {
        "amount": 5000,
        "risk_tolerance": "medium"
    })
    print(f"  Input: amount=5000, risk_tolerance='medium'")
    print(f"  Output: {financial_result}")
    
    print("\n✓ Domain logic is modular and pluggable")
    print("✓ Each domain can have its own rules and databases")

def demo_knowledge_gaps():
    """Demonstrate explicit knowledge gap detection"""
    print_section("4. KNOWLEDGE GAP DETECTION")
    
    print("ISRE explicitly identifies missing knowledge instead of hallucinating.\n")
    
    # Create knowledge engine with limited knowledge
    engine = KnowledgeQueryEngine()
    engine.update_knowledge("apple", {"category": "fruit"})
    engine.update_knowledge("run", {"category": "action"})
    # Note: "unicorn" and "teleport" are NOT in the knowledge base
    
    # Create a reasoning decision with some unknown concepts
    path = ReasoningPath(
        id="test_path",
        steps=[
            IntentNode(
                id="node1",
                type=IntentType.GOAL,
                semantic_payload=[
                    SemanticPrimitive(id="p1", concept="apple"),
                    SemanticPrimitive(id="p2", concept="unicorn")  # Unknown!
                ]
            ),
            IntentNode(
                id="node2",
                type=IntentType.GOAL,
                semantic_payload=[
                    SemanticPrimitive(id="p3", concept="teleport")  # Unknown!
                ]
            )
        ]
    )
    
    decision = ReasoningDecision(
        selected_path=path,
        justification="Test decision",
        confidence=0.8,
        alternative_paths=[]
    )
    
    # Detect gaps
    detector = KnowledgeGapDetector(engine)
    gaps = detector.detect_gaps(decision)
    
    print("Reasoning Path Concepts:")
    print("-" * 45)
    print("  Known: apple, run")
    print("  Unknown: unicorn, teleport")
    
    print("\nKnowledge Gap Detection:")
    print("-" * 45)
    print(f"  Detected Gaps: {gaps}")
    
    print("\n✓ System explicitly identifies missing knowledge")
    print("✓ No hallucination - gaps are flagged, not fabricated")
    print("✓ User can be prompted for clarification or additional data")

def demo_separation_of_concerns():
    """Demonstrate separation between reasoning and knowledge"""
    print_section("5. SEPARATION OF REASONING AND KNOWLEDGE")
    
    print("ISRE maintains strict separation between reasoning logic and knowledge.\n")
    
    engine = KnowledgeQueryEngine()
    
    print("Scenario: Updating Knowledge Without Retraining")
    print("-" * 45)
    
    # Initial knowledge
    engine.update_knowledge("pluto", {"status": "planet"})
    result1 = engine.query("pluto")
    print(f"  Initial: Pluto status = {result1.content['status']}")
    
    # Update knowledge (like real-world scientific consensus changed)
    engine.update_knowledge("pluto", {"status": "dwarf_planet"})
    result2 = engine.query("pluto")
    print(f"  Updated: Pluto status = {result2.content['status']}")
    
    print("\n  ✓ Knowledge updated instantly")
    print("  ✓ No model retraining required")
    print("  ✓ Reasoning engine unchanged")
    
    print("\nComparison with LLMs:")
    print("-" * 45)
    print("  LLM Approach:")
    print("    - Knowledge embedded in weights")
    print("    - Requires retraining to update facts")
    print("    - Can't distinguish reasoning from knowledge")
    print("    - May hallucinate outdated information")
    
    print("\n  ISRE Approach:")
    print("    - Knowledge in external databases")
    print("    - Update facts in real-time")
    print("    - Clear separation of concerns")
    print("    - Flags missing knowledge explicitly")

def main():
    """Run all demonstrations"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ISRE LAYER 4: WORLD KNOWLEDGE INTEGRATION".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    print("\nThis demonstration shows how ISRE integrates external knowledge")
    print("dynamically, rather than embedding it in model weights.")
    
    input("\nPress Enter to begin...")
    
    demo_dynamic_knowledge_query()
    input("\nPress Enter to continue...")
    
    demo_physics_rules()
    input("\nPress Enter to continue...")
    
    demo_domain_logic()
    input("\nPress Enter to continue...")
    
    demo_knowledge_gaps()
    input("\nPress Enter to continue...")
    
    demo_separation_of_concerns()
    
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  DEMONSTRATION COMPLETE".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80 + "\n")
    
    print("Key Takeaways:")
    print("  ✓ Knowledge is queried dynamically from external sources")
    print("  ✓ Physics rules are pluggable external modules")
    print("  ✓ Domain-specific logic is modular and extensible")
    print("  ✓ Knowledge gaps are explicitly detected (no hallucination)")
    print("  ✓ Clear separation between reasoning and knowledge")
    print("  ✓ Knowledge can be updated in real-time without retraining")
    
    print("\nFor more details, see:")
    print("  • docs/TECHNICAL_VALIDATION.md")
    print("  • docs/COMPLETE_VALIDATION_SUMMARY.md")
    print("  • tests/test_knowledge.py\n")

if __name__ == "__main__":
    main()
