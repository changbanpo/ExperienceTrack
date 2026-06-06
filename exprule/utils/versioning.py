"""
Version management for experiences.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience


class ExperienceVersionManager:
    """
    Manages versioning for experiences.
    """

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage
        self._version_history: Dict[str, List[Dict[str, Any]]] = {}

    def save_version(self, experience: Experience, message: Optional[str] = None) -> None:
        """
        Save a version snapshot of an experience.
        """
        from exprule.utils.serialization import serialize_experience
        
        if experience.experience_id not in self._version_history:
            self._version_history[experience.experience_id] = []
            
        snapshot = {
            "version": experience.version,
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "data": serialize_experience(experience, format="dict")
        }
        self._version_history[experience.experience_id].append(snapshot)

    def get_version(self, experience_id: str, version: int) -> Optional[Experience]:
        """
        Get a specific version of an experience.
        """
        from exprule.utils.serialization import deserialize_experience
        
        if experience_id not in self._version_history:
            return None
            
        history = self._version_history[experience_id]
        for snapshot in history:
            if snapshot["version"] == version:
                return deserialize_experience(snapshot["data"], format="dict")
        return None

    def list_versions(self, experience_id: str) -> List[Dict[str, Any]]:
        """List all versions of an experience."""
        if experience_id not in self._version_history:
            return []
        return [
            {
                "version": h["version"],
                "timestamp": h["timestamp"],
                "message": h["message"]
            }
            for h in self._version_history[experience_id]
        ]

    def rollback(self, experience_id: str, version: int) -> Optional[Experience]:
        """
        Rollback an experience to a previous version.
        """
        old_exp = self.get_version(experience_id, version)
        if old_exp:
            old_exp.increment_version()
            self.storage.save_experience(old_exp)
            self.save_version(old_exp, f"Rollback to version {version}")
            return old_exp
        return None
