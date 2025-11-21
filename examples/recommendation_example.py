"""
Recommendation Engine Example
Demonstrates 7-step recommendation pipeline
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Recommendation import RecommendationEngine, RecommendationConfig


async def main():
    """Main example function"""
    
    print("=" * 80)
    print("Recommendation Engine - 7-Step Pipeline Example")
    print("=" * 80)
    print()
    
    # 1. Create configuration
    print("1. Creating Configuration...")
    config = RecommendationConfig(
        candidate_pool_size=1500,
        exploration_strategy="epsilon_greedy",
        epsilon=0.1
    )
    print("✓ Configuration created")
    print()
    
    # 2. Initialize engine
    print("2. Initializing Recommendation Engine...")
    engine = RecommendationEngine(config)
    print("✓ Engine initialized")
    print()
    
    # 3. Generate recommendations for multiple users
    print("3. Generating Recommendations...")
    user_ids = ["agent_001", "agent_002", "agent_003"]
    
    for user_id in user_ids:
        print(f"\n   User: {user_id}")
        
        # Get recommendations
        response = await engine.recommend(
            user_id=user_id,
            num_results=10,
            context={"device": "mobile", "time": "evening"}
        )
        
        print(f"   ✓ Generated {len(response.recommendations)} recommendations")
        print(f"   ✓ Latency: {response.latency * 1000:.1f}ms")
        print(f"   ✓ Pipeline metadata:")
        for key, value in response.metadata.items():
            print(f"      - {key}: {value}")
        
        # Show sample recommendations
        print(f"   ✓ Sample recommendations:")
        for i, rec in enumerate(response.recommendations[:3], 1):
            print(f"      {i}. {rec.get('id')}: {rec.get('text', '')[:50]}...")
            print(f"         Utility: {rec.get('utility', 0):.3f}, Safety: {rec.get('safety_score', 0):.3f}")
    
    print()
    
    # 4. Record interactions
    print("4. Recording Interactions...")
    await engine.record_interaction(
        user_id="agent_001",
        content_id="content_001",
        interaction_type="like",
        dwell_time=15.5
    )
    await engine.record_interaction(
        user_id="agent_002",
        content_id="content_002",
        interaction_type="share",
        dwell_time=30.0
    )
    print("✓ Interactions recorded")
    print()
    
    # 5. Get statistics
    print("5. Engine Statistics:")
    stats = engine.get_statistics()
    print(f"   - Total requests: {stats['total_requests']}")
    print(f"   - Average latency: {stats['average_latency_ms']:.1f}ms")
    print(f"   - Cache size: {stats['cache_size']}")
    print()
    
    # 6. Test caching
    print("6. Testing Cache...")
    response_cached = await engine.recommend(user_id="agent_001", num_results=10)
    print(f"   ✓ Cached response: {response_cached.metadata.get('cached', False)}")
    print(f"   ✓ Latency: {response_cached.latency * 1000:.1f}ms (should be faster)")
    print()
    
    print("=" * 80)
    print("Recommendation Example Complete!")
    print("=" * 80)
    print()
    print("7-Step Pipeline:")
    print("  1. Candidate Sourcing ✓")
    print("  2. Light Ranking ✓")
    print("  3. Heavy Ranking ✓")
    print("  4. Exploration ✓")
    print("  5. Diversity Injection ✓")
    print("  6. Safety Filtering ✓")
    print("  7. Serving ✓")
    print()


if __name__ == "__main__":
    asyncio.run(main())

