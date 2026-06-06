"""
Feedback model for experience rules.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FeedbackType(str, Enum):
    """
    Type of feedback signal.
    """

    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    QUALITY_SCORE = "quality_score"
    TIME_SAVED = "time_saved"


class Feedback(BaseModel):
    """
    Feedback model for updating experience weights.
    """

    feedback_id: str = Field(..., description="Unique feedback identifier")
    experience_id: str = Field(..., description="Experience being evaluated")
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Feedback score (0-1)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feedback timestamp")
    contributor_id: Optional[str] = Field(None, description="Contributor of the feedback")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional feedback details")
    execution_time_ms: Optional[float] = Field(None, description="Execution time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "feedback_id": "fb_001",
                    "experience_id": "exp_001",
                    "feedback_type": "success",
                    "score": 0.9,
                    "contributor_id": "agent_01",
                    "execution_time_ms": 1200.0,
                }
            ]
        }
    }

    def get_learning_signal(self) -> float:
        """
        Convert feedback to a learning signal value.
        """
        if self.feedback_type == FeedbackType.SUCCESS:
            return max(self.score, 0.5)
        elif self.feedback_type == FeedbackType.FAILURE:
            return min(self.score, 0.5)
        elif self.feedback_type == FeedbackType.PARTIAL:
            return self.score
        elif self.feedback_type == FeedbackType.QUALITY_SCORE:
            return self.score
        elif self.feedback_type == FeedbackType.TIME_SAVED:
            return min(1.0, max(0.0, self.score))
        return 0.5
