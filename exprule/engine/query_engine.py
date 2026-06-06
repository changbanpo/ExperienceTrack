"""
Query engine for searching and recommending experiences.
"""

from typing import List, Optional, Tuple
from exprule.storage.base import BaseStorage
from exprule.core.experience import Experience
from exprule.core.context import Context


class QueryEngine:
    """
    Engine for querying and recommending experiences.
    """

    def __init__(self, storage: BaseStorage) -> None:
        self.storage = storage

    def _calculate_relevance_score(self, experience: Experience, context: Optional[Context] = None) -> float:
        """Calculate relevance score combining weight, usage, and context similarity."""
        score = experience.task.weight * 0.4
        usage_factor = min(1.0, experience.task.usage_count / 100.0)
        score += usage_factor * 0.3
        if context:
            ctx_similarity = 0.0
            if experience.task.tags:
                ctx_tags = set(context.tags)
                exp_tags = set(experience.task.tags)
                if ctx_tags and exp_tags:
                    ctx_similarity = len(ctx_tags & exp_tags) / len(ctx_tags | exp_tags)
            score += ctx_similarity * 0.3
        return min(1.0, score)

    def query(
        self,
        query: str,
        context: Optional[Context] = None,
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None,
        limit: int = 10,
        min_weight: float = 0.0
    ) -> List[Tuple[Experience, float]]:
        """
        Query experiences and return ranked results with relevance scores.
        
        Args:
            query: Search query string
            context: Optional current context for relevance scoring
            tags: Optional tags to filter by
            domain: Optional domain to filter by
            limit: Maximum number of results to return
            min_weight: Minimum weight threshold for results
            
        Returns:
            List of (Experience, relevance_score) tuples sorted by relevance
        """
        candidates = self.storage.search_experiences(query, tags, domain)
        scored_candidates: List[Tuple[Experience, float]] = []
        
        for exp in candidates:
            if not exp.is_active:
                continue
            if exp.task.weight < min_weight:
                continue
            score = self._calculate_relevance_score(exp, context)
            scored_candidates.append((exp, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:limit]

    def get_best_experience(
        self,
        query: str,
        context: Optional[Context] = None,
        tags: Optional[List[str]] = None,
        domain: Optional[str] = None
    ) -> Optional[Experience]:
        """Get the single best matching experience."""
        results = self.query(query, context, tags, domain, limit=1)
        return results[0][0] if results else None

    def list_popular(self, limit: int = 10, domain: Optional[str] = None) -> List[Experience]:
        """List popular experiences by usage count."""
        all_exps = self.storage.list_experiences(limit=1000)
        filtered = [exp for exp in all_exps if exp.is_active and (domain is None or exp.task.domain == domain)]
        filtered.sort(key=lambda x: x.task.usage_count, reverse=True)
        return filtered[:limit]

    def list_high_success(self, limit: int = 10, min_success_rate: float = 0.7) -> List[Experience]:
        """List experiences with high success rates."""
        all_exps = self.storage.list_experiences(limit=1000)
        filtered = [exp for exp in all_exps if exp.is_active and exp.task.weight >= min_success_rate]
        filtered.sort(key=lambda x: x.task.weight, reverse=True)
        return filtered[:limit]
