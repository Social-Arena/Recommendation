"""
Recommendation Engine
Twitter-inspired 7-step recommendation pipeline
"""

__version__ = "0.1.0"

from .core.recommendation_engine import RecommendationEngine
from .config.rec_config import RecommendationConfig

__all__ = [
    '__version__',
    'RecommendationEngine',
    'RecommendationConfig',
]

