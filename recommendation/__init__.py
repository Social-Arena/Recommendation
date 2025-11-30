"""
Social Arena Recommendation System

The central mediator between agents and feeds that controls information flow,
shapes agent behavior, and determines network dynamics.
"""

from .base import RecommendationSystem, RecommendationMetrics
from .system import CentralizedRecommendationSystem
from .strategies import (
    ChronologicalStrategy,
    EngagementStrategy,
    InterestStrategy,
    CollaborativeStrategy,
    BalancedStrategy,
    RandomStrategy
)

__all__ = [
    'RecommendationSystem',
    'RecommendationMetrics',
    'CentralizedRecommendationSystem',
    'ChronologicalStrategy',
    'EngagementStrategy',
    'InterestStrategy',
    'CollaborativeStrategy',
    'BalancedStrategy',
    'RandomStrategy',
]

__version__ = '1.0.0'

