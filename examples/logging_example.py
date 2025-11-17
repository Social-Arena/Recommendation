"""
Example demonstrating how to integrate the logging system
into recommendation engine components.

This example shows:
1. Basic logging usage
2. Performance tracking with decorators
3. Error logging with stack traces
4. Request context management
5. Structured data logging
"""

import asyncio
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any

# Import logging utilities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.logger import get_logger, LogContext, set_log_context
from utils.decorators import log_performance, log_errors, trace_execution


# Example 1: Basic Logging
class CandidateGenerator:
    """Example candidate generator with basic logging."""

    def __init__(self):
        # Get a logger for this component
        self.logger = get_logger(__name__, component="candidate", level="DEBUG")

    def generate_candidates(self, user_id: str, count: int = 100) -> List[str]:
        """Generate candidate items for a user."""

        # Log the operation start
        self.logger.info(
            f"Starting candidate generation for user {user_id}",
            extra={
                "user_id": user_id,
                "requested_count": count,
                "operation": "candidate_generation"
            }
        )

        # Simulate candidate generation
        candidates = [f"item_{i}" for i in range(count)]

        # Log the result
        self.logger.info(
            f"Generated {len(candidates)} candidates",
            extra={
                "user_id": user_id,
                "generated_count": len(candidates),
                "operation": "candidate_generation"
            }
        )

        return candidates


# Example 2: Performance Tracking with Decorators
class Ranker:
    """Example ranker with automatic performance tracking."""

    def __init__(self):
        self.logger = get_logger(__name__, component="ranking", level="DEBUG")

    @log_performance(log_args=True, log_result=False)
    def rank_candidates(self, user_id: str, candidates: List[str]) -> List[str]:
        """Rank candidates for a user."""

        self.logger.debug(
            f"Ranking {len(candidates)} candidates",
            extra={
                "user_id": user_id,
                "candidate_count": len(candidates)
            }
        )

        # Simulate ranking (add random delays)
        import time
        time.sleep(random.uniform(0.01, 0.05))

        # Simple random ranking
        ranked = random.sample(candidates, len(candidates))

        return ranked[:10]  # Return top 10


# Example 3: Error Handling with Logging
class DiversityInjector:
    """Example diversity injector with error logging."""

    def __init__(self):
        self.logger = get_logger(__name__, component="diversity", level="DEBUG")

    @log_errors(reraise=True)
    def inject_diversity(self, ranked_items: List[str]) -> List[str]:
        """Inject diversity into ranked items."""

        self.logger.info(
            "Applying diversity injection",
            extra={"item_count": len(ranked_items)}
        )

        # Simulate potential error
        if random.random() < 0.1:  # 10% chance of error
            self.logger.warning(
                "Low diversity detected",
                extra={"diversity_score": 0.3}
            )
            raise ValueError("Insufficient diversity in candidates")

        # Apply diversity logic
        diverse_items = ranked_items  # Simplified

        self.logger.info(
            "Diversity injection completed",
            extra={
                "original_count": len(ranked_items),
                "diverse_count": len(diverse_items)
            }
        )

        return diverse_items


# Example 4: Async Functions with Full Tracing
class RecommendationService:
    """Example recommendation service with full tracing."""

    def __init__(self):
        self.logger = get_logger(__name__, component="serving", level="DEBUG")
        self.candidate_generator = CandidateGenerator()
        self.ranker = Ranker()
        self.diversity_injector = DiversityInjector()

    @trace_execution(component="serving")
    async def get_recommendations(self, user_id: str, num_items: int = 10) -> Dict[str, Any]:
        """
        Generate recommendations for a user.

        This function demonstrates full execution tracing with:
        - Entry/exit logging
        - Performance measurement
        - Error handling
        """

        self.logger.info(
            f"Processing recommendation request",
            extra={
                "user_id": user_id,
                "num_items": num_items,
                "request_type": "recommendation"
            }
        )

        # Step 1: Generate candidates
        candidates = self.candidate_generator.generate_candidates(user_id, count=100)

        # Step 2: Rank candidates
        ranked = self.ranker.rank_candidates(user_id, candidates)

        # Step 3: Apply diversity
        try:
            diverse = self.diversity_injector.inject_diversity(ranked)
        except ValueError as e:
            self.logger.error(
                "Diversity injection failed, using fallback",
                exc_info=True,
                extra={
                    "user_id": user_id,
                    "fallback_strategy": "top_ranked"
                }
            )
            diverse = ranked  # Fallback

        # Simulate async processing
        await asyncio.sleep(0.01)

        result = {
            "user_id": user_id,
            "recommendations": diverse[:num_items],
            "total_candidates": len(candidates),
            "timestamp": datetime.utcnow().isoformat()
        }

        self.logger.info(
            "Recommendation request completed",
            extra={
                "user_id": user_id,
                "num_recommendations": len(result['recommendations']),
                "success": True
            }
        )

        return result


# Example 5: Request Context Management
async def process_user_request(user_id: str, request_id: str = None):
    """
    Example showing how to use request context for tracing.

    All logs within this context will include the request_id
    and user_id, making it easy to trace the request flow.
    """

    if request_id is None:
        request_id = str(uuid.uuid4())

    # Use context manager to set logging context
    with LogContext(request_id=request_id, user_id=user_id):
        logger = get_logger(__name__, component="app")

        logger.info(
            "Processing user request",
            extra={
                "request_type": "recommendation",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Create service
        service = RecommendationService()

        # Get recommendations
        try:
            recommendations = await service.get_recommendations(user_id, num_items=10)

            logger.info(
                "Request completed successfully",
                extra={
                    "num_recommendations": len(recommendations['recommendations']),
                    "duration_context": "within_context"
                }
            )

            return recommendations

        except Exception as e:
            logger.error(
                f"Request failed: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }
            )
            raise


# Example 6: Performance-Critical Section
class FeatureExtractor:
    """Example showing trace-level logging for detailed debugging."""

    def __init__(self):
        self.logger = get_logger(__name__, component="ranking", level="TRACE")

    def extract_features(self, user_id: str, item_id: str) -> Dict[str, float]:
        """Extract features with detailed trace logging."""

        # Use TRACE level for very detailed debugging
        self.logger.trace(
            f"Starting feature extraction",
            extra={
                "user_id": user_id,
                "item_id": item_id
            }
        )

        features = {}

        # Trace each feature extraction step
        self.logger.trace("Extracting user features", extra={"user_id": user_id})
        features['user_activity'] = random.random()

        self.logger.trace("Extracting item features", extra={"item_id": item_id})
        features['item_popularity'] = random.random()

        self.logger.trace("Calculating interaction features", extra={
            "user_id": user_id,
            "item_id": item_id
        })
        features['interaction_score'] = random.random()

        self.logger.trace(
            "Feature extraction completed",
            extra={
                "feature_count": len(features),
                "features": features
            }
        )

        return features


# Main demonstration
async def main():
    """Run demonstration of logging system."""

    print("="*80)
    print("Recommendation Engine Logging System Demonstration")
    print("="*80)
    print("\nThis demo will generate sample logs in trace/logs/")
    print("You can analyze them using the log analysis tools.\n")

    # Simulate multiple user requests
    users = [f"user_{i}" for i in range(5)]

    for user_id in users:
        request_id = str(uuid.uuid4())

        print(f"Processing request for {user_id} (request_id: {request_id})")

        try:
            recommendations = await process_user_request(user_id, request_id)
            print(f"  ✓ Success: {len(recommendations['recommendations'])} recommendations")
        except Exception as e:
            print(f"  ✗ Error: {type(e).__name__}: {str(e)}")

        # Add some delay between requests
        await asyncio.sleep(0.1)

    print("\n" + "="*80)
    print("Demonstration complete!")
    print("="*80)
    print("\nGenerated logs can be found in:")
    print("  - trace/logs/candidate/candidate.log")
    print("  - trace/logs/ranking/ranking.log")
    print("  - trace/logs/diversity/diversity.log")
    print("  - trace/logs/serving/serving.log")
    print("  - trace/logs/errors/ (for error logs)")
    print("  - trace/logs/performance/ (for performance metrics)")
    print("\nTo analyze logs, use:")
    print("  python utils/log_analyzer.py trace <request_id>")
    print("  python utils/trace_request.py <request_id>")
    print("="*80 + "\n")


if __name__ == '__main__':
    asyncio.run(main())
