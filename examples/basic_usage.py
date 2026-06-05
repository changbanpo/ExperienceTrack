#!/usr/bin/env python3
"""
Basic Usage Example
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from exprule.agents.base_agent import BaseAgentAdapter


def main():
    print("=== exprule Basic Usage Example\n")

    # 1. Create agent adapter
    agent = BaseAgentAdapter(agent_id="example_agent")
    print("Created agent adapter")

    # 2. Create an experience
    print("\n=== Creating and recording an experience...")
    experience = agent.create_simple_experience(
        task_name="Calculate Factorial",
        description="Calculate the factorial of a number",
        goal="Compute n! for a given integer n",
        tags=["math", "factorial", "python"],
        domain="mathematics",
        steps=[
            {
                "name": "Input Validation",
                "description": "Check that input is a non-negative integer",
                "actions": [
                    {"name": "Check Type", "description": "Verify input is integer"},
                    {"name": "Check Sign", "description": "Verify input >= 0"}
                ]
            },
            {
                "name": "Compute Result",
                "description": "Calculate factorial using iterative approach",
                "actions": [
                    {"name": "Initialize Result", "description": "Start with result = 1"},
                    {"name": "Multiply Iteratively", "description": "Multiply from 2 to n"}
                ]
            }
        ]
    )
    agent.record_experience(experience)
    print(f"Recorded experience with ID: {experience.experience_id}")

    # 3. Query for experience
    print("\n=== Querying for experience...")
    found = agent.query_experience("factorial math")
    if found:
        print(f"Found: {found.task.task_name} (weight: {found.task.weight:.2f})")
        print(f"  Description: {found.task.description}")

    # 4. Update feedback
    print("\n=== Recording successful usage...")
    for _ in range(5):
        updated = agent.update_feedback(experience.experience_id, success=True)
    if updated:
        print(f"Updated weight: {updated.task.weight:.4f}")

    # 5. Query all experiences
    print("\n=== All experiences...")
    all_exps = agent.query_all_experiences("math", limit=10)
    for exp in all_exps:
        print(f"  - {exp.task.task_name} (w={exp.task.weight:.2f}, used={exp.task.usage_count})")


if __name__ == "__main__":
    main()
