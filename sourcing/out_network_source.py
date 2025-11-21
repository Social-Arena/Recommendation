"""
Out-of-Network Source - Content from interest clusters and trending
"""

from typing import List, Dict, Any
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class OutOfNetworkSource:
    """Out-of-network content source"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("out_network_source")
        
        # Mock interest clusters
        self.interest_clusters: Dict[str, List[str]] = {}
        self.trending_content: List[Dict[str, Any]] = []
    
    async def generate_candidates(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """
        Generate out-of-network candidates
        
        Args:
            user_id: User ID
            limit: Number of candidates
            
        Returns:
            List of out-of-network content
        """
        candidates = []
        
        # Interest-based content (60% of out-of-network)
        interest_limit = int(limit * 0.6)
        interest_content = self._get_interest_based_content(user_id, interest_limit)
        candidates.extend(interest_content)
        
        # Trending content (30% of out-of-network)
        trending_limit = int(limit * 0.3)
        trending = self._get_trending_content(trending_limit)
        candidates.extend(trending)
        
        # Similar users content (10% of out-of-network)
        similar_limit = limit - len(candidates)
        similar_content = self._get_similar_users_content(user_id, similar_limit)
        candidates.extend(similar_content)
        
        self.logger.debug(f"Out-of-network candidates generated", extra={
            "user_id": user_id,
            "candidate_count": len(candidates)
        })
        
        return candidates[:limit]
    
    def _get_interest_based_content(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get content based on user interests"""
        # Mock interest-based content
        user_interests = self._get_user_interests(user_id)
        
        content = []
        for i in range(limit):
            content.append({
                "id": f"interest_content_{user_id}_{i}",
                "author_id": f"author_interest_{i}",
                "text": f"Content about {random.choice(user_interests)}",
                "source": "out_network_interest",
                "engagement_count": random.randint(50, 5000),
                "topics": [random.choice(user_interests)],
                "created_at": "2025-11-20T00:00:00Z"
            })
        
        return content
    
    def _get_trending_content(self, limit: int) -> List[Dict[str, Any]]:
        """Get trending content"""
        # Mock trending content
        trending_topics = ["AI", "Tech", "Innovation", "Viral", "Breaking"]
        
        content = []
        for i in range(limit):
            content.append({
                "id": f"trending_{i}",
                "author_id": f"influencer_{i}",
                "text": f"Trending: {random.choice(trending_topics)}",
                "source": "out_network_trending",
                "engagement_count": random.randint(1000, 10000),
                "topics": [random.choice(trending_topics)],
                "is_trending": True,
                "created_at": "2025-11-20T00:00:00Z"
            })
        
        return content
    
    def _get_similar_users_content(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get content from similar users"""
        # Mock similar users content
        content = []
        for i in range(limit):
            content.append({
                "id": f"similar_{user_id}_{i}",
                "author_id": f"similar_author_{i}",
                "text": "Content from similar user",
                "source": "out_network_similar",
                "engagement_count": random.randint(20, 500),
                "topics": [f"topic_{random.randint(1, 10)}"],
                "created_at": "2025-11-20T00:00:00Z"
            })
        
        return content
    
    def _get_user_interests(self, user_id: str) -> List[str]:
        """Get user interests"""
        # Mock interests
        return ["technology", "AI", "programming", "innovation"]

