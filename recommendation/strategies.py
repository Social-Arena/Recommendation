"""
Different recommendation strategies.

Each strategy implements a different algorithm for ranking and filtering content.
"""

from typing import List, Dict, Any
from datetime import datetime
import random
from collections import Counter

import logging

logger = logging.getLogger(__name__)


class ChronologicalStrategy:
    """Show most recent posts from followed users (Twitter 2010 style)."""
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Rank by creation time, newest first."""
        logger.debug("Ranking feeds chronologically", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds)
        })
        
        return sorted(
            feeds,
            key=lambda f: getattr(f, 'created_at', ''),
            reverse=True
        )


class EngagementStrategy:
    """Show posts with highest engagement (Facebook algorithm style)."""
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Rank by engagement score."""
        logger.debug("Ranking feeds by engagement", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds)
        })
        
        def engagement_score(feed):
            metrics = getattr(feed, 'public_metrics', None)
            if metrics:
                return (
                    getattr(metrics, 'like_count', 0) * 1 +
                    getattr(metrics, 'retweet_count', 0) * 2 +
                    getattr(metrics, 'reply_count', 0) * 3 +
                    getattr(metrics, 'quote_count', 0) * 2
                )
            return 0
        
        return sorted(feeds, key=engagement_score, reverse=True)


class InterestStrategy:
    """Show posts matching agent's interests (content-based filtering)."""
    
    def __init__(self):
        self.agent_interests: Dict[str, List[str]] = {}
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Rank by interest matching."""
        logger.debug("Ranking feeds by interests", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds)
        })
        
        # Get agent interests from context or learn from history
        interests = context.get('agent_metadata', {}).get('interests', [])
        if not interests:
            interests = self._infer_interests(agent_id, context)
        
        def interest_score(feed):
            text = getattr(feed, 'text', '').lower()
            return sum(1 for interest in interests if interest.lower() in text)
        
        return sorted(feeds, key=interest_score, reverse=True)
    
    def _infer_interests(self, agent_id: str, context: Dict[str, Any]) -> List[str]:
        """Infer interests from agent's action history."""
        # Extract topics from liked/replied feeds
        actions = context.get('actions', [])
        liked_topics = []
        
        for action in actions:
            if action['action'] in ['like', 'reply']:
                # Would need to look up the feed content here
                pass
        
        return liked_topics or ['general']


class CollaborativeStrategy:
    """Show posts liked by similar agents (Netflix-style collaborative filtering)."""
    
    def __init__(self):
        self.agent_similarities: Dict[str, Dict[str, float]] = {}
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Rank by collaborative filtering."""
        logger.debug("Ranking feeds collaboratively", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds)
        })
        
        # Find similar agents
        similar_agents = self._find_similar_agents(agent_id, context)
        
        # Get what similar agents liked
        similar_agent_likes = self._get_similar_agent_preferences(similar_agents, context)
        
        def collab_score(feed):
            feed_id = getattr(feed, 'id', None)
            return similar_agent_likes.get(feed_id, 0)
        
        return sorted(feeds, key=collab_score, reverse=True)
    
    def _find_similar_agents(self, agent_id: str, context: Dict[str, Any]) -> List[str]:
        """Find agents with similar behavior."""
        # Simplified: agents who follow similar users
        following = set(context.get('following', []))
        
        # Would compare with other agents' following lists
        # For now, return empty
        return []
    
    def _get_similar_agent_preferences(
        self,
        similar_agents: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, int]:
        """Get feed preferences from similar agents."""
        preferences = Counter()
        # Would aggregate likes from similar agents
        return dict(preferences)


class BalancedStrategy:
    """
    Balance exploration vs exploitation.
    
    - 80% exploit: Content we know the agent likes
    - 20% explore: New content to broaden their feed
    """
    
    def __init__(self, explore_ratio: float = 0.2):
        self.explore_ratio = explore_ratio
        self.engagement_strategy = EngagementStrategy()
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Rank with exploration-exploitation balance."""
        logger.debug("Ranking feeds with balanced strategy", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds),
            "explore_ratio": self.explore_ratio
        })
        
        if not feeds:
            return []
        
        # Split into exploit and explore
        exploit_count = int(len(feeds) * (1 - self.explore_ratio))
        explore_count = len(feeds) - exploit_count
        
        # Exploit: Use engagement ranking
        exploit_feeds = self.engagement_strategy.rank_feeds(feeds, agent_id, context)[:exploit_count]
        
        # Explore: Random sample from remaining
        remaining = [f for f in feeds if f not in exploit_feeds]
        explore_feeds = random.sample(remaining, min(explore_count, len(remaining)))
        
        # Interleave exploit and explore
        result = []
        for i in range(max(len(exploit_feeds), len(explore_feeds))):
            if i < len(exploit_feeds):
                result.append(exploit_feeds[i])
            if i < len(explore_feeds):
                result.append(explore_feeds[i])
        
        return result


class RandomStrategy:
    """Random baseline - show random feeds."""
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """Random shuffle."""
        logger.debug("Ranking feeds randomly", extra={
            "agent_id": agent_id,
            "feed_count": len(feeds)
        })
        
        shuffled = feeds.copy()
        random.shuffle(shuffled)
        return shuffled

