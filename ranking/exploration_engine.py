"""
Exploration Engine - Balance exploitation and exploration
"""

from typing import List, Dict, Any
import random
import math

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class ExplorationEngine:
    """Exploration engine - applies exploration strategies"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("exploration_engine")
        
        # Track content impressions for UCB
        self.content_stats: Dict[str, Dict[str, Any]] = {}
        self.total_impressions = 0
    
    async def apply_exploration(self, ranked: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Apply exploration strategy
        
        Args:
            ranked: Ranked content
            user_id: User ID
            
        Returns:
            Exploration-adjusted ranking
        """
        strategy = self.config.exploration_strategy
        
        if strategy == "epsilon_greedy":
            result = self._epsilon_greedy(ranked)
        elif strategy == "ucb":
            result = self._ucb(ranked)
        elif strategy == "thompson_sampling":
            result = self._thompson_sampling(ranked)
        else:
            result = ranked
        
        self.logger.debug(f"Exploration applied", extra={
            "user_id": user_id,
            "strategy": strategy,
            "explored_count": len(result)
        })
        
        return result
    
    def _epsilon_greedy(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ε-greedy exploration"""
        explored = ranked.copy()
        
        for i in range(len(explored)):
            if random.random() < self.config.epsilon:
                # Add exploration bonus
                explored[i]["utility"] = explored[i].get("utility", 0.5) + random.uniform(0.1, 0.5)
        
        # Re-sort
        explored.sort(key=lambda x: x.get("utility", 0), reverse=True)
        
        return explored
    
    def _ucb(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Upper Confidence Bound exploration"""
        explored = []
        
        for content in ranked:
            content_id = content.get("id", "")
            
            # Get stats
            if content_id not in self.content_stats:
                self.content_stats[content_id] = {
                    "impressions": 0,
                    "total_reward": 0.0
                }
            
            stats = self.content_stats[content_id]
            
            # Calculate UCB
            if stats["impressions"] == 0:
                ucb_score = float('inf')  # Always try new content
            else:
                mean_reward = stats["total_reward"] / stats["impressions"]
                exploration_bonus = self.config.ucb_confidence * math.sqrt(
                    math.log(self.total_impressions + 1) / stats["impressions"]
                )
                ucb_score = mean_reward + exploration_bonus
            
            content["ucb_score"] = ucb_score
            content["utility"] = ucb_score
            explored.append(content)
        
        # Sort by UCB score
        explored.sort(key=lambda x: x.get("ucb_score", 0), reverse=True)
        
        return explored
    
    def _thompson_sampling(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Thompson sampling exploration"""
        import numpy as np
        
        explored = []
        
        for content in ranked:
            content_id = content.get("id", "")
            
            # Get stats
            if content_id not in self.content_stats:
                self.content_stats[content_id] = {
                    "successes": 1,
                    "failures": 1
                }
            
            stats = self.content_stats[content_id]
            
            # Sample from Beta distribution
            sample = np.random.beta(stats["successes"], stats["failures"])
            
            content["thompson_sample"] = sample
            content["utility"] = sample
            explored.append(content)
        
        # Sort by sampled value
        explored.sort(key=lambda x: x.get("thompson_sample", 0), reverse=True)
        
        return explored
    
    def record_impression(self, content_id: str, engagement: bool, reward: float = 0.0) -> None:
        """Record content impression for learning"""
        if content_id not in self.content_stats:
            self.content_stats[content_id] = {
                "impressions": 0,
                "total_reward": 0.0,
                "successes": 1,
                "failures": 1
            }
        
        stats = self.content_stats[content_id]
        stats["impressions"] += 1
        stats["total_reward"] += reward
        
        if engagement:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        
        self.total_impressions += 1

