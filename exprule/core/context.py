"""
Context model for experience rules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Context(BaseModel):
    """
    Environment context model.
    Captures the environment state when an experience was created or used.
    """

    context_id: str = Field(..., description="Unique identifier for the context")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Context timestamp")
    user_id: Optional[str] = Field(None, description="User identifier")
    system_state: Dict[str, Any] = Field(default_factory=dict, description="System state")
    environment: Dict[str, Any] = Field(default_factory=dict, description="Environment details")
    tags: List[str] = Field(default_factory=list, description="Context tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "context_id": "ctx_001",
                    "user_id": "user_123",
                    "system_state": {"os": "linux", "python_version": "3.10"},
                    "environment": {"time_of_day": "morning", "task_type": "coding"},
                    "tags": ["coding", "linux"],
                }
            ]
        }
    }

    def similarity_score(self, other: "Context") -> float:
        """
        Calculate similarity score between two contexts.
        """
        score = 0.0
        if self.user_id and other.user_id and self.user_id == other.user_id:
            score += 0.2
        tag_overlap = len(set(self.tags) & set(other.tags))
        tag_union = len(set(self.tags) | set(other.tags))
        if tag_union > 0:
            score += 0.3 * (tag_overlap / tag_union)
        if self.environment.keys() & other.environment.keys():
            env_score = 0.0
            for key in self.environment.keys() & other.environment.keys():
                if self.environment[key] == other.environment[key]:
                    env_score += 0.1
            score += min(0.5, env_score)
        return min(1.0, score)
