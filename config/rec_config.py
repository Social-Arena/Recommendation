"""
Recommendation Engine Configuration
"""

from typing import Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RecommendationConfig:
    """Configuration for recommendation engine"""
    
    # Candidate sourcing
    candidate_pool_size: int = 1500
    in_network_ratio: float = 0.4
    out_network_ratio: float = 0.5
    social_proof_ratio: float = 0.1
    
    # Ranking
    light_ranking_top_k: int = 500
    heavy_ranking_top_k: int = 100
    
    # Exploration
    exploration_strategy: str = "epsilon_greedy"  # epsilon_greedy, ucb, thompson_sampling
    epsilon: float = 0.1
    ucb_confidence: float = 2.0
    
    # Diversity
    max_same_author: int = 2
    max_topic_repetition: float = 0.3
    min_topic_diversity: int = 5
    
    # Safety
    safety_threshold: float = 0.7
    enable_toxicity_filter: bool = True
    enable_spam_filter: bool = True
    
    # Serving
    cache_ttl: int = 300  # seconds
    target_latency_ms: int = 100
    
    # A/B testing
    enable_ab_testing: bool = True
    default_experiment_duration: int = 7  # days
    
    # Model configuration
    user_embedding_dim: int = 128
    content_embedding_dim: int = 128
    hidden_dim: int = 256
    
    # Trace logging
    log_level: str = "INFO"
    trace_dir: Path = field(default_factory=lambda: Path("trace"))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "candidate_pool_size": self.candidate_pool_size,
            "in_network_ratio": self.in_network_ratio,
            "out_network_ratio": self.out_network_ratio,
            "social_proof_ratio": self.social_proof_ratio,
            "light_ranking_top_k": self.light_ranking_top_k,
            "heavy_ranking_top_k": self.heavy_ranking_top_k,
            "exploration_strategy": self.exploration_strategy,
            "epsilon": self.epsilon,
            "ucb_confidence": self.ucb_confidence,
            "max_same_author": self.max_same_author,
            "max_topic_repetition": self.max_topic_repetition,
            "min_topic_diversity": self.min_topic_diversity,
            "safety_threshold": self.safety_threshold,
            "enable_toxicity_filter": self.enable_toxicity_filter,
            "enable_spam_filter": self.enable_spam_filter,
            "cache_ttl": self.cache_ttl,
            "target_latency_ms": self.target_latency_ms,
            "enable_ab_testing": self.enable_ab_testing,
            "default_experiment_duration": self.default_experiment_duration
        }


def get_default_config() -> RecommendationConfig:
    """Get default recommendation configuration"""
    return RecommendationConfig()

