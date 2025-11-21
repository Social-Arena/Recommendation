"""
Social Proof Source - Content friends engaged with
"""

from typing import List, Dict, Any
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class SocialProofSource:
    """Social proof content source"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("social_proof_source")
        
        # Mock social graph
        self.friend_graph: Dict[str, List[str]] = {}
    
    async def generate_candidates(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate social proof candidates
        
        Args:
            user_id: User ID
            limit: Number of candidates
            
        Returns:
            List of content friends engaged with
        """
        candidates = []
        
        # Get user's friends
        friends = self._get_friends(user_id)
        
        # Get content friends engaged with
        for friend_id in friends[:10]:  # Limit to 10 friends
            friend_content = self._get_friend_engagements(friend_id, limit // max(len(friends[:10]), 1))
            candidates.extend(friend_content)
        
        self.logger.debug(f"Social proof candidates generated", extra={
            "user_id": user_id,
            "friend_count": len(friends),
            "candidate_count": len(candidates)
        })
        
        return candidates[:limit]
    
    def _get_friends(self, user_id: str) -> List[str]:
        """Get user's friends"""
        # Mock: 5-15 friends
        if user_id not in self.friend_graph:
            num_friends = random.randint(5, 15)
            self.friend_graph[user_id] = [f"friend_{i}" for i in range(num_friends)]
        
        return self.friend_graph[user_id]
    
    def _get_friend_engagements(self, friend_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get content friend engaged with"""
        # Mock friend engagements
        content = []
        for i in range(min(limit, 5)):
            content.append({
                "id": f"social_{friend_id}_{i}",
                "author_id": f"author_{i}",
                "text": f"Content {friend_id} liked",
                "source": "social_proof",
                "engagement_count": random.randint(100, 2000),
                "topics": [f"topic_{random.randint(1, 10)}"],
                "friend_engagement": {
                    "friend_id": friend_id,
                    "engagement_type": random.choice(["like", "share", "comment"])
                },
                "created_at": "2025-11-20T00:00:00Z"
            })
        
        return content

