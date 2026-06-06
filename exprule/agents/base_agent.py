"""
Base agent adapter for integrating with exprule.
"""

from typing import Optional, List, Dict, Any
from exprule.storage.base import BaseStorage
from exprule.storage.memory import MemoryStorage
from exprule.core.experience import Experience, Task, Step, Action
from exprule.core.context import Context
from exprule.engine.query_engine import QueryEngine
from exprule.engine.update_engine import UpdateEngine


class BaseAgentAdapter:
    """
    Base adapter for integrating agents with the experience rule system.
    Provides a simple API for querying, recording, and updating experiences.
    """

    def __init__(
        self,
        storage: Optional[BaseStorage] = None,
        agent_id: str = "default_agent"
    ) -> None:
        self.storage = storage or MemoryStorage()
        self.query_engine = QueryEngine(self.storage)
        self.update_engine = UpdateEngine(self.storage)
        self.agent_id = agent_id

    def query_experience(
        self,
        query: str,
        context: Optional[Context] = None,
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None
    ) -> Optional[Experience]:
        """
        Query for relevant experience.
        
        Args:
            query: Search query
            context: Optional current context
            tags: Optional tags to filter
            domain: Optional domain to filter
            
        Returns:
            Best matching experience or None
        """
        return self.query_engine.get_best_experience(query, context, tags, domain)

    def query_all_experiences(
        self,
        query: str,
        context: Optional[Context] = None,
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None,
        limit: int = 10
    ) -> List[Experience]:
        """
        Query for multiple relevant experiences.
        
        Returns:
            List of experiences sorted by relevance
        """
        results = self.query_engine.query(query, context, tags, domain, limit=limit)
        return [exp for exp, _ in results]

    def record_experience(self, experience: Experience) -> None:
        """
        Record a new experience.
        
        Args:
            experience: Experience to record
        """
        experience.task.contributor_id = self.agent_id
        self.storage.save_experience(experience)

    def update_feedback(self, experience_id: str, success: bool) -> Optional[Experience]:
        """
        Update feedback for an experience.
        
        Args:
            experience_id: ID of the experience
            success: Whether the experience was successful
            
        Returns:
            Updated experience or None
        """
        if success:
            return self.update_engine.record_success(experience_id, self.agent_id)
        else:
            return self.update_engine.record_failure(experience_id, self.agent_id)

    def create_simple_experience(
        self,
        task_name: str,
        description: str,
        goal: str,
        steps: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None
    ) -> Experience:
        """
        Helper to create a simple experience quickly.
        
        Args:
            task_name: Name of the task
            description: Description
            goal: Goal of the task
            steps: Optional list of step dicts
            tags: Optional tags
            domain: Optional domain
            
        Returns:
            Created Experience object
        """
        step_objects: List[Step] = []
        if steps:
            for i, step_data in enumerate(steps):
                step = Step(
                    step_name=step_data.get("name", f"Step {i+1}"),
                    description=step_data.get("description", ""),
                    order=i
                )
                if "actions" in step_data:
                    for action_data in step_data["actions"]:
                        action = Action(
                            action_name=action_data.get("name", "Action"),
                            description=action_data.get("description", "")
                        )
                        step.actions.append(action)
                step_objects.append(step)
        
        task = Task(
            task_name=task_name,
            description=description,
            goal=goal,
            steps=step_objects,
            tags=tags or [],
            domain=domain,
            contributor_id=self.agent_id
        )
        
        experience = Experience(task=task)
        return experience
