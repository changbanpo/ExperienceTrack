"""
Base storage interface for experience rules.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from exprule.core.experience import Experience
from exprule.core.context import Context
from exprule.core.feedback import Feedback


class BaseStorage(ABC):
    """Abstract base class for experience storage engines."""

    @abstractmethod
    def save_experience(self, experience: Experience) -> None:
        """Save an experience to storage."""
        pass

    @abstractmethod
    def get_experience(self, experience_id: str) -> Optional[Experience]:
        """Retrieve an experience by ID."""
        pass

    @abstractmethod
    def delete_experience(self, experience_id: str) -> bool:
        """Delete an experience from storage. Return True if deleted."""
        pass

    @abstractmethod
    def list_experiences(self, limit: int = 100, offset: int = 0) -> List[Experience]:
        """List experiences with pagination."""
        pass

    @abstractmethod
    def search_experiences(
        self, query: str, tags: Optional[List[str]] = None, domain: Optional[str] = None
    ) -> List[Experience]:
        """Search experiences by query, tags, or domain."""
        pass

    @abstractmethod
    def save_context(self, context: Context) -> None:
        """Save a context to storage."""
        pass

    @abstractmethod
    def get_context(self, context_id: str) -> Optional[Context]:
        """Retrieve a context by ID."""
        pass

    @abstractmethod
    def save_feedback(self, feedback: Feedback) -> None:
        """Save feedback to storage."""
        pass

    @abstractmethod
    def get_feedbacks_for_experience(self, experience_id: str) -> List[Feedback]:
        """Get all feedbacks for an experience."""
        pass

    @abstractmethod
    def get_experience_count(self) -> int:
        """Get total number of experiences."""
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Clear all stored data."""
        pass
