"""
Core experience models: Task, Step, Action (three-layer structure).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid4())


class BaseExperienceNode(BaseModel):
    """Base class for all experience nodes."""

    node_id: str = Field(default_factory=generate_id, description="Unique node identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    contributor_id: Optional[str] = Field(None, description="Contributor identifier")
    version: int = Field(default=1, ge=1, description="Version number")
    weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Success rate/weight")
    usage_count: int = Field(default=0, ge=0, description="Number of times used")
    success_count: int = Field(default=0, ge=0, description="Number of successful uses")
    context_conditions: Dict[str, Any] = Field(default_factory=dict, description="Applicable context conditions")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    domain: Optional[str] = Field(None, description="Domain/category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def update_weight_from_feedback(self, success: bool) -> None:
        """Update weight based on success/failure feedback."""
        self.usage_count += 1
        if success:
            self.success_count += 1
        self.weight = self.success_count / self.usage_count if self.usage_count > 0 else 0.5
        self.update_timestamp()


class Action(BaseExperienceNode):
    """
    Micro-level: specific action or tool call.
    """

    action_name: str = Field(..., description="Name of the action")
    description: str = Field(..., description="Description of the action")
    tool_name: Optional[str] = Field(None, description="Tool being called")
    input_params: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    output_result: Dict[str, Any] = Field(default_factory=dict, description="Output result")
    execution_status: str = Field(default="pending", description="Execution status")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class Step(BaseExperienceNode):
    """
    Middle-level: step in a task decomposition.
    """

    step_name: str = Field(..., description="Name of the step")
    description: str = Field(..., description="Description of the step")
    order: int = Field(..., ge=0, description="Execution order")
    preconditions: List[str] = Field(default_factory=list, description="Preconditions")
    postconditions: List[str] = Field(default_factory=list, description="Postconditions")
    actions: List[Action] = Field(default_factory=list, description="Actions in this step")
    average_success_rate: float = Field(default=0.5, ge=0.0, le=1.0, description="Average success rate")
    estimated_duration_ms: Optional[float] = Field(None, description="Estimated duration in milliseconds")


class Task(BaseExperienceNode):
    """
    Macro-level: task goal and success criteria.
    """

    task_name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Description of the task")
    goal: str = Field(..., description="Task goal")
    success_criteria: List[str] = Field(default_factory=list, description="Success criteria")
    steps: List[Step] = Field(default_factory=list, description="Steps to complete the task")
    context_requirements: Dict[str, Any] = Field(default_factory=dict, description="Context requirements")
    alternative_approaches: List[str] = Field(default_factory=list, description="Alternative approach IDs")


class Experience(BaseModel):
    """
    Complete experience container with three-layer structure.
    """

    experience_id: str = Field(default_factory=generate_id, description="Unique experience identifier")
    task: Task = Field(..., description="Macro-level task")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    version: int = Field(default=1, ge=1, description="Experience version")
    is_active: bool = Field(default=True, description="Whether the experience is active")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def get_all_nodes(self) -> List[BaseExperienceNode]:
        """Get all nodes in this experience (task, steps, actions)."""
        nodes: List[BaseExperienceNode] = [self.task]
        for step in self.task.steps:
            nodes.append(step)
            nodes.extend(step.actions)
        return nodes

    def increment_version(self) -> None:
        """Increment the experience version."""
        self.version += 1
        self.update_timestamp()
