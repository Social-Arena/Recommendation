"""
In-Network Source - Content from followed authors
"""

from typing import List, Dict, Any
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class InNetworkSource:
    """In-network content source - content from followed authors"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("in_network_source")
        
        # Mock following graph
        self.following_graph: Dict[str, List[str]] = {}
    
    async def generate_candidates(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate in-network candidates
        
        Args:
            user_id: User ID
            limit: Number of candidates to generate
            
        Returns:
            List of candidate content from followed authors
        """
        candidates = []
        
        # Get authors user follows (mock)
        following = self._get_following(user_id)
        
        # Generate content from followed authors
        for author_id in following:
            # Mock content from this author
            author_content = self._get_author_content(author_id, limit // max(len(following), 1))
            candidates.extend(author_content)
        
        self.logger.debug(f"In-network candidates generated", extra={
            "user_id": user_id,
            "following_count": len(following),
            "candidate_count": len(candidates)
        })
        
        return candidates[:limit]
    
    def _get_following(self, user_id: str) -> List[str]:
        """Get list of authors user follows"""
        # Mock: return 10-20 followed authors
        if user_id not in self.following_graph:
            num_following = random.randint(10, 20)
            self.following_graph[user_id] = [f"author_{i}" for i in range(num_following)]
        
        return self.following_graph[user_id]
    
    def _get_author_content(self, author_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get recent content from author"""
        # Mock content generation
        content = []
        for i in range(min(limit, 10)):
            content.append({
                "id": f"content_{author_id}_{i}",
                "author_id": author_id,
                "text": f"Content from {author_id}",
                "source": "in_network",
                "engagement_count": random.randint(10, 1000),
                "topics": [f"topic_{random.randint(1, 10)}"],
                "created_at": "2025-11-20T00:00:00Z"
            })
        
        return content

