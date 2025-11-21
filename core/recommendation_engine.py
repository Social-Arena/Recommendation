"""
Recommendation Engine - Main orchestrator for 7-step pipeline
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.sourcing.candidate_sourcing import CandidateSourcing
from Recommendation.ranking.light_ranker import LightRanker
from Recommendation.ranking.heavy_ranker import HeavyRanker
from Recommendation.ranking.exploration_engine import ExplorationEngine
from Recommendation.ranking.diversity_injector import DiversityInjector
from Recommendation.filters.safety_filter import SafetyFilter
from Recommendation.utils.logger import get_logger


class RecommendationResponse:
    """Recommendation response"""
    
    def __init__(self, recommendations: List[Any], latency: float, metadata: Dict[str, Any]):
        self.recommendations = recommendations
        self.latency = latency
        self.metadata = metadata


class RecommendationEngine:
    """
    Main recommendation engine orchestrating 7-step pipeline
    
    Steps:
    1. Candidate Sourcing (In-Network, Out-of-Network, Social Proof)
    2. Light Ranking
    3. Heavy Ranking (Multi-Task)
    4. Exploration
    5. Diversity Injection
    6. Safety Filtering
    7. Real-time Serving
    """
    
    def __init__(self, config: Optional[RecommendationConfig] = None):
        self.config = config or RecommendationConfig()
        self.logger = get_logger("recommendation_engine")
        
        # Initialize pipeline components
        self.candidate_sourcing = CandidateSourcing(self.config)
        self.light_ranker = LightRanker(self.config)
        self.heavy_ranker = HeavyRanker(self.config)
        self.exploration_engine = ExplorationEngine(self.config)
        self.diversity_injector = DiversityInjector(self.config)
        self.safety_filter = SafetyFilter(self.config)
        
        # Cache for recommendations
        self.cache: Dict[str, Any] = {}
        
        # Metrics
        self.request_count = 0
        self.total_latency = 0.0
        
        self.logger.info("RecommendationEngine initialized", extra={
            "config": self.config.to_dict()
        })
    
    async def recommend(
        self,
        user_id: str,
        num_results: int = 100,
        context: Optional[Dict[str, Any]] = None
    ) -> RecommendationResponse:
        """
        Generate recommendations for user
        
        Args:
            user_id: User/Agent ID
            num_results: Number of recommendations to return
            context: Additional context (device, time, etc.)
            
        Returns:
            RecommendationResponse with recommendations and metadata
        """
        start_time = time.time()
        
        self.logger.info(f"Generating recommendations", extra={
            "user_id": user_id,
            "num_results": num_results,
            "request_id": f"req_{self.request_count}"
        })
        
        # Check cache
        cache_key = f"{user_id}:{num_results}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < self.config.cache_ttl:
                self.logger.debug(f"Cache hit", extra={"user_id": user_id})
                return RecommendationResponse(
                    recommendations=cached["recommendations"],
                    latency=time.time() - start_time,
                    metadata={"cached": True}
                )
        
        # Step 1: Candidate Sourcing
        candidates = await self.candidate_sourcing.generate_candidates(user_id)
        self.logger.debug(f"Candidates sourced", extra={
            "user_id": user_id,
            "candidate_count": len(candidates)
        })
        
        # Step 2: Light Ranking
        light_ranked = await self.light_ranker.rank(candidates, user_id)
        self.logger.debug(f"Light ranking complete", extra={
            "user_id": user_id,
            "ranked_count": len(light_ranked)
        })
        
        # Step 3: Heavy Ranking
        heavy_ranked = await self.heavy_ranker.rank(light_ranked, user_id)
        self.logger.debug(f"Heavy ranking complete", extra={
            "user_id": user_id,
            "ranked_count": len(heavy_ranked)
        })
        
        # Step 4: Exploration
        explored = await self.exploration_engine.apply_exploration(heavy_ranked, user_id)
        self.logger.debug(f"Exploration applied", extra={
            "user_id": user_id,
            "strategy": self.config.exploration_strategy
        })
        
        # Step 5: Diversity Injection
        diversified = await self.diversity_injector.inject_diversity(explored)
        self.logger.debug(f"Diversity injected", extra={
            "user_id": user_id,
            "diversified_count": len(diversified)
        })
        
        # Step 6: Safety Filtering
        filtered = await self.safety_filter.filter(diversified)
        self.logger.debug(f"Safety filtering complete", extra={
            "user_id": user_id,
            "filtered_count": len(filtered),
            "removed": len(diversified) - len(filtered)
        })
        
        # Step 7: Final results
        final_recommendations = filtered[:num_results]
        
        latency = time.time() - start_time
        
        # Update metrics
        self.request_count += 1
        self.total_latency += latency
        
        # Cache results
        self.cache[cache_key] = {
            "recommendations": final_recommendations,
            "timestamp": time.time()
        }
        
        self.logger.info(f"Recommendations generated", extra={
            "user_id": user_id,
            "count": len(final_recommendations),
            "latency_ms": latency * 1000,
            "request_id": f"req_{self.request_count}"
        })
        
        return RecommendationResponse(
            recommendations=final_recommendations,
            latency=latency,
            metadata={
                "cached": False,
                "pipeline_steps": 7,
                "candidate_count": len(candidates),
                "filtered_count": len(diversified) - len(filtered)
            }
        )
    
    async def record_interaction(
        self,
        user_id: str,
        content_id: str,
        interaction_type: str,
        **kwargs
    ) -> None:
        """
        Record user interaction with content
        
        Args:
            user_id: User ID
            content_id: Content ID
            interaction_type: Type of interaction (like, share, view, etc.)
            **kwargs: Additional interaction data
        """
        self.logger.info(f"Interaction recorded", extra={
            "user_id": user_id,
            "content_id": content_id,
            "interaction_type": interaction_type,
            **kwargs
        })
        
        # In production, this would update ML models
        # For now, just log
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get recommendation statistics"""
        return {
            "total_requests": self.request_count,
            "average_latency_ms": (self.total_latency / max(self.request_count, 1)) * 1000,
            "cache_size": len(self.cache)
        }

