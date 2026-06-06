"""
Update engine for experience weights using Q-learning.
"""

from typing import Optional
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience
from exprule.core.feedback import Feedback, FeedbackType


class UpdateEngine:
    """
    Engine for updating experience weights based on feedback.
    Implements symbolic Q-learning for weight updates.
    """

    def __init__(
        self,
        storage: BaseStorage,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        decay_threshold: int = 10,
        min_weight: float = 0.01
    ) -> None:
        self.storage = storage
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.decay_threshold = decay_threshold
        self.min_weight = min_weight

    def apply_feedback(self, feedback: Feedback) -> Optional[Experience]:
        """
        Apply feedback to update experience weights.
        
        Args:
            feedback: Feedback to apply
            
        Returns:
            Updated experience if found, None otherwise
        """
        experience = self.storage.get_experience(feedback.experience_id)
        if not experience:
            return None

        self.storage.save_feedback(feedback)
        learning_signal = feedback.get_learning_signal()

        self._update_node_weights(experience.task, learning_signal)
        for step in experience.task.steps:
            self._update_node_weights(step, learning_signal)
            for action in step.actions:
                self._update_node_weights(action, learning_signal)

        experience.update_timestamp()
        self.storage.save_experience(experience)
        return experience

    def _update_node_weights(self, node, learning_signal: float) -> None:
        """Update a single node's weight using Q-learning."""
        old_weight = node.weight
        new_weight = old_weight + self.learning_rate * (learning_signal - old_weight)
        node.weight = max(self.min_weight, min(1.0, new_weight))
        node.update_timestamp()

        if learning_signal > 0.7:
            node.usage_count += 1
            node.success_count += 1
        elif learning_signal < 0.3:
            node.usage_count += 1

    def record_success(self, experience_id: str, contributor_id: Optional[str] = None) -> Optional[Experience]:
        """Record a successful execution."""
        feedback = Feedback(
            feedback_id=f"fb_success_{experience_id}",
            experience_id=experience_id,
            feedback_type=FeedbackType.SUCCESS,
            score=1.0,
            contributor_id=contributor_id
        )
        return self.apply_feedback(feedback)

    def record_failure(self, experience_id: str, contributor_id: Optional[str] = None) -> Optional[Experience]:
        """Record a failed execution."""
        feedback = Feedback(
            feedback_id=f"fb_failure_{experience_id}",
            experience_id=experience_id,
            feedback_type=FeedbackType.FAILURE,
            score=0.0,
            contributor_id=contributor_id
        )
        return self.apply_feedback(feedback)

    def deactivate_low_quality(self, min_success_rate: float = 0.2, min_usage: int = 5) -> int:
        """Deactivate experiences with low success rates."""
        all_exps = self.storage.list_experiences(limit=10000)
        deactivated = 0
        for exp in all_exps:
            if exp.is_active and exp.task.usage_count >= min_usage and exp.task.weight < min_success_rate:
                exp.is_active = False
                self.storage.save_experience(exp)
                deactivated += 1
        return deactivated
