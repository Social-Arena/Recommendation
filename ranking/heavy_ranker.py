"""
Heavy Ranker - Precise ranking with multi-task model
"""

from typing import List, Dict, Any
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class MultiTaskModel:
    """Multi-task prediction model"""
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict multiple engagement probabilities
        
        Returns:
            Dictionary of predictions
        """
        # Mock predictions - in production, use trained neural network
        return {
            "p_like": random.uniform(0.1, 0.9),
            "p_retweet": random.uniform(0.05, 0.5),
            "p_reply": random.uniform(0.02, 0.3),
            "p_click": random.uniform(0.1, 0.7),
            "expected_dwell_time": random.uniform(1.0, 30.0),
            "p_negative": random.uniform(0.01, 0.1)
        }


class UtilityScorer:
    """Compute utility score from multi-task predictions"""
    
    def score(self, predictions: Dict[str, float], user_preferences: Dict[str, float]) -> float:
        """
        Compute utility score
        
        Args:
            predictions: Multi-task predictions
            user_preferences: User preference weights
            
        Returns:
            Utility score
        """
        # Default weights
        weights = {
            "like": 1.0,
            "retweet": 2.0,
            "reply": 3.0,
            "click": 1.5,
            "dwell_time": 0.1,
            "negative": -5.0
        }
        
        # Override with user preferences if available
        if user_preferences:
            weights.update(user_preferences)
        
        # Calculate utility
        utility = (
            predictions["p_like"] * weights["like"] +
            predictions["p_retweet"] * weights["retweet"] +
            predictions["p_reply"] * weights["reply"] +
            predictions["p_click"] * weights["click"] +
            predictions["expected_dwell_time"] * weights["dwell_time"] +
            predictions["p_negative"] * weights["negative"]
        )
        
        return utility


class HeavyRanker:
    """Heavy ranker - precise ranking with multi-task model"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("heavy_ranker")
        
        self.multi_task_model = MultiTaskModel()
        self.utility_scorer = UtilityScorer()
    
    async def rank(self, candidates: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Rank candidates using heavy model
        
        Args:
            candidates: Candidate content
            user_id: User ID
            
        Returns:
            Ranked candidates
        """
        ranked = []
        
        # Get user preferences
        user_preferences = self._get_user_preferences(user_id)
        
        for candidate in candidates:
            # Extract deep features
            features = self._extract_deep_features(candidate, user_id)
            
            # Multi-task predictions
            predictions = self.multi_task_model.predict(features)
            
            # Compute utility score
            utility = self.utility_scorer.score(predictions, user_preferences)
            
            # Add to candidate
            candidate["predictions"] = predictions
            candidate["utility"] = utility
            ranked.append(candidate)
        
        # Sort by utility
        ranked.sort(key=lambda x: x["utility"], reverse=True)
        
        self.logger.debug(f"Heavy ranking complete", extra={
            "user_id": user_id,
            "input_count": len(candidates),
            "output_count": len(ranked[:self.config.heavy_ranking_top_k])
        })
        
        return ranked[:self.config.heavy_ranking_top_k]
    
    def _extract_deep_features(self, candidate: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Extract deep features for multi-task model"""
        # Mock deep features
        return {
            "content_id": candidate.get("id"),
            "user_id": user_id,
            "text_embedding": [random.random() for _ in range(128)],  # Mock embedding
            "user_embedding": [random.random() for _ in range(128)],
            "engagement_count": candidate.get("engagement_count", 0),
            "author_influence": random.uniform(0, 1),
            "content_age": random.uniform(0, 48),
            "topic_match": random.uniform(0, 1)
        }
    
    def _get_user_preferences(self, user_id: str) -> Dict[str, float]:
        """Get user preference weights"""
        # Mock user preferences
        return {
            "like": 1.0,
            "retweet": 2.0,
            "reply": 3.0
        }

