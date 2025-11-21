"""
Light Ranker - Fast initial ranking with lightweight features
"""

from typing import List, Dict, Any
from datetime import datetime
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class LightRanker:
    """Light ranker - fast ranking with lightweight features"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("light_ranker")
    
    async def rank(self, candidates: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Rank candidates using lightweight features
        
        Args:
            candidates: Candidate content list
            user_id: User ID
            
        Returns:
            Ranked candidates
        """
        ranked = []
        
        for candidate in candidates:
            # Extract lightweight features
            features = self._extract_light_features(candidate, user_id)
            
            # Compute light score
            score = self._compute_light_score(features)
            
            # Add score to candidate
            candidate["light_score"] = score
            ranked.append(candidate)
        
        # Sort by light score
        ranked.sort(key=lambda x: x["light_score"], reverse=True)
        
        self.logger.debug(f"Light ranking complete", extra={
            "user_id": user_id,
            "input_count": len(candidates),
            "output_count": len(ranked[:self.config.light_ranking_top_k])
        })
        
        return ranked[:self.config.light_ranking_top_k]
    
    def _extract_light_features(self, candidate: Dict[str, Any], user_id: str) -> Dict[str, float]:
        """Extract lightweight features"""
        # Content age
        age_hours = random.uniform(0, 48)  # Mock age
        age_score = max(0, 1 - age_hours / 48)
        
        # Engagement velocity
        engagement = candidate.get("engagement_count", 0)
        velocity_score = min(engagement / 1000, 1.0)
        
        # Author influence
        author_followers = random.randint(100, 100000)  # Mock
        influence_score = min(author_followers / 100000, 1.0)
        
        # User-content match
        match_score = random.uniform(0.3, 0.9)  # Mock matching
        
        return {
            "age_score": age_score,
            "velocity_score": velocity_score,
            "influence_score": influence_score,
            "match_score": match_score
        }
    
    def _compute_light_score(self, features: Dict[str, float]) -> float:
        """Compute light ranking score"""
        # Weighted combination
        score = (
            features["age_score"] * 0.2 +
            features["velocity_score"] * 0.3 +
            features["influence_score"] * 0.2 +
            features["match_score"] * 0.3
        )
        
        return score

