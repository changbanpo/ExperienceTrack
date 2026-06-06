"""
In-memory storage implementation for experience rules.
"""

from typing import Dict, List, Optional
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience
from exprule.core.context import Context
from exprule.core.feedback import Feedback


class MemoryStorage(BaseStorage):
    """In-memory storage using dictionaries."""

    def __init__(self) -> None:
        self._experiences: Dict[str, Experience] = {}
        self._contexts: Dict[str, Context] = {}
        self._feedbacks: Dict[str, List[Feedback]] = {}

    def save_experience(self, experience: Experience) -> None:
        self._experiences[experience.experience_id] = experience

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        return self._experiences.get(experience_id)

    def delete_experience(self, experience_id: str) -> bool:
        if experience_id in self._experiences:
            del self._experiences[experience_id]
            if experience_id in self._feedbacks:
                del self._feedbacks[experience_id]
            return True
        return False

    def list_experiences(self, limit: int = 100, offset: int = 0) -> List[Experience]:
        values = list(self._experiences.values())
        return values[offset:offset + limit]

    def search_experiences(
        self, query: str, tags: Optional[List[str]] = None, domain: Optional[str] = None
    ) -> List[Experience]:
        results: List[Experience] = []
        query_lower = query.lower()
        for exp in self._experiences.values():
            match = False
            if query_lower in exp.task.task_name.lower() or query_lower in exp.task.description.lower():
                match = True
            if tags:
                exp_tags = set(exp.task.tags)
                if not exp_tags & set(tags):
                    match = False
            if domain and exp.task.domain != domain:
                match = False
            if match:
                results.append(exp)
        return results

    def save_context(self, context: Context) -> None:
        self._contexts[context.context_id] = context

    def get_context(self, context_id: str) -> Optional[Context]:
        return self._contexts.get(context_id)

    def save_feedback(self, feedback: Feedback) -> None:
        if feedback.experience_id not in self._feedbacks:
            self._feedbacks[feedback.experience_id] = []
        self._feedbacks[feedback.experience_id].append(feedback)

    def get_feedbacks_for_experience(self, experience_id: str) -> List[Feedback]:
        return self._feedbacks.get(experience_id, [])

    def get_experience_count(self) -> int:
        return len(self._experiences)

    def clear_all(self) -> None:
        self._experiences.clear()
        self._contexts.clear()
        self._feedbacks.clear()
