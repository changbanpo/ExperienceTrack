"""
Abstraction engine for creating generalized experiences.
"""

from typing import List, Optional
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience, Task, Step, Action


class AbstractionEngine:
    """
    Engine for abstracting and generalizing experiences.
    """

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def find_similar_experiences(self, experience: Experience, threshold: float = 0.7) -> List[Experience]:
        """Find experiences similar to the given one."""
        all_exps = self.storage.list_experiences(limit=1000)
        similar: List[Experience] = []
        
        for exp in all_exps:
            if exp.experience_id == experience.experience_id:
                continue
            if not exp.is_active:
                continue
            if exp.task.domain != experience.task.domain:
                continue
                
            similarity = self._calculate_experience_similarity(experience, exp)
            if similarity >= threshold:
                similar.append(exp)
                
        return similar

    def _calculate_experience_similarity(self, exp1: Experience, exp2: Experience) -> float:
        """Calculate similarity between two experiences."""
        score = 0.0
        
        tags1 = set(exp1.task.tags)
        tags2 = set(exp2.task.tags)
        if tags1 and tags2:
            tag_overlap = len(tags1 & tags2) / len(tags1 | tags2)
            score += tag_overlap * 0.4
            
        steps1 = len(exp1.task.steps)
        steps2 = len(exp2.task.steps)
        if steps1 > 0 and steps2 > 0:
            step_ratio = min(steps1, steps2) / max(steps1, steps2)
            score += step_ratio * 0.3
            
        name1 = exp1.task.task_name.lower()
        name2 = exp2.task.task_name.lower()
        words1 = set(name1.split())
        words2 = set(name2.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / len(words1 | words2)
            score += word_overlap * 0.3
            
        return score

    def create_generalized_experience(
        self,
        experiences: List[Experience],
        task_name: str,
        description: str,
        goal: str
    ) -> Optional[Experience]:
        """Create a generalized experience from multiple similar experiences."""
        if not experiences:
            return None
            
        avg_weight = sum(exp.task.weight for exp in experiences) / len(experiences)
        avg_usage = sum(exp.task.usage_count for exp in experiences) // len(experiences)
        avg_success = sum(exp.task.success_count for exp in experiences) // len(experiences)
        
        all_tags = set()
        for exp in experiences:
            all_tags.update(exp.task.tags)
            
        generalized_task = Task(
            task_name=task_name,
            description=description,
            goal=goal,
            tags=list(all_tags),
            domain=experiences[0].task.domain,
            weight=avg_weight,
            usage_count=avg_usage,
            success_count=avg_success
        )
        
        generalized_exp = Experience(
            task=generalized_task,
            metadata={
                "generalized_from": [exp.experience_id for exp in experiences],
                "generalization_count": len(experiences)
            }
        )
        
        self.storage.save_experience(generalized_exp)
        return generalized_exp

    def merge_experiences(self, main_id: str, other_ids: List[str]) -> Optional[Experience]:
        """Merge multiple experiences into one."""
        main_exp = self.storage.get_experience(main_id)
        if not main_exp:
            return None
            
        others = [self.storage.get_experience(oid) for oid in other_ids]
        others = [o for o in others if o is not None]
        
        if not others:
            return None
            
        all_exps = [main_exp] + others
        return self.create_generalized_experience(
            all_exps,
            main_exp.task.task_name,
            main_exp.task.description,
            main_exp.task.goal
        )
