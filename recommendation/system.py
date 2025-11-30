"""
Core recommendation system implementation.
"""

from typing import Dict, List, Any, Set, Optional
from datetime import datetime
from collections import defaultdict, Counter
import random
from pydantic import BaseModel

import logging

logger = logging.getLogger(__name__)


class CentralizedRecommendationSystem:
    """
    Centralized recommendation system - the platform algorithm.
    
    This system maintains global state and controls what each agent sees.
    It's the "Twitter algorithm" or "Facebook algorithm" of Social Arena.
    """
    
    def __init__(self, strategy: Optional[Any] = None):
        """
        Initialize the recommendation system.
        
        Args:
            strategy: Recommendation strategy to use (defaults to chronological)
        """
        # Global state
        self.feed_pool: List[Any] = []
        self.agent_pool: Dict[str, Dict[str, Any]] = {}
        self.social_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Temporal state
        self.current_timestamp = datetime.utcnow()
        self.feed_history: Dict[str, List[str]] = defaultdict(list)
        
        # Behavioral state
        self.agent_actions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.engagement_signals: Dict[str, Dict[str, Any]] = defaultdict(lambda: defaultdict(int))
        
        # Strategy
        self.strategy = strategy
        
        # Statistics
        self.stats = {
            "total_feeds": 0,
            "total_agents": 0,
            "total_actions": 0,
            "total_follows": 0,
        }
        
        logger.info("Initialized CentralizedRecommendationSystem", extra={
            "strategy": str(type(strategy).__name__) if strategy else "None"
        })
    
    def ingest_feed(self, feed: Any) -> None:
        """
        Add new feed to the global pool.
        
        Args:
            feed: Feed object to ingest
        """
        self.feed_pool.append(feed)
        self.stats["total_feeds"] += 1
        
        # Update engagement signals
        feed_id = getattr(feed, 'id', None)
        author_id = getattr(feed, 'author_id', None)
        
        logger.info("Ingested new feed", extra={
            "feed_id": feed_id,
            "author_id": author_id,
            "total_feeds": len(self.feed_pool)
        })
    
    def fetch(self, agent_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Return personalized content for a specific agent.
        
        Args:
            agent_id: Agent requesting content
            context: Additional context
        
        Returns:
            Personalized content dictionary
        """
        context = context or {}
        
        logger.debug(f"Fetching content for agent {agent_id}", extra={
            "agent_id": agent_id,
            "context": context
        })
        
        # Get candidate feeds
        candidate_feeds = self._get_candidate_feeds(agent_id, context)
        
        # Apply strategy if available
        if self.strategy:
            ranked_feeds = self.strategy.rank_feeds(
                candidate_feeds,
                agent_id,
                self._get_agent_context(agent_id, context)
            )
        else:
            # Default: chronological
            ranked_feeds = sorted(
                candidate_feeds,
                key=lambda f: getattr(f, 'created_at', ''),
                reverse=True
            )
        
        # Limit to top N
        max_feeds = context.get('max_feeds', 20)
        ranked_feeds = ranked_feeds[:max_feeds]
        
        # Record what we showed
        for feed in ranked_feeds:
            feed_id = getattr(feed, 'id', None)
            if feed_id:
                self.feed_history[agent_id].append(feed_id)
        
        # Get suggestions
        suggested_users = self._suggest_users(agent_id, context)
        trending_topics = self._get_trending_topics(context)
        
        result = {
            "feeds": ranked_feeds,
            "users": suggested_users,
            "trends": trending_topics,
            "metadata": {
                "strategy": str(type(self.strategy).__name__) if self.strategy else "chronological",
                "candidate_count": len(candidate_feeds),
                "returned_count": len(ranked_feeds),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        logger.info(f"Fetched content for agent {agent_id}", extra={
            "agent_id": agent_id,
            "feed_count": len(ranked_feeds),
            "candidate_count": len(candidate_feeds)
        })
        
        return result
    
    def record_action(
        self,
        agent_id: str,
        action: str,
        target_id: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Record agent action for learning.
        
        Args:
            agent_id: Agent performing action
            action: Action type
            target_id: Target of action
            metadata: Additional metadata
        """
        metadata = metadata or {}
        
        action_record = {
            "agent_id": agent_id,
            "action": action,
            "target_id": target_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata
        }
        
        self.agent_actions[agent_id].append(action_record)
        self.stats["total_actions"] += 1
        
        # Update engagement signals
        self.engagement_signals[target_id][action] += 1
        
        logger.debug(f"Recorded action: {action}", extra={
            "agent_id": agent_id,
            "action": action,
            "target_id": target_id
        })
    
    def add_agent(self, agent_id: str, metadata: Dict[str, Any] = None) -> None:
        """
        Register a new agent.
        
        Args:
            agent_id: Agent identifier
            metadata: Agent metadata
        """
        self.agent_pool[agent_id] = metadata or {}
        self.stats["total_agents"] += 1
        
        logger.info(f"Added agent {agent_id}", extra={
            "agent_id": agent_id,
            "total_agents": len(self.agent_pool)
        })
    
    def update_social_graph(
        self,
        follower_id: str,
        following_id: str,
        action: str = "follow"
    ) -> None:
        """
        Update social graph.
        
        Args:
            follower_id: Agent following
            following_id: Agent being followed
            action: "follow" or "unfollow"
        """
        if action == "follow":
            self.social_graph[follower_id].add(following_id)
            self.stats["total_follows"] += 1
            
            logger.info(f"{follower_id} followed {following_id}", extra={
                "follower_id": follower_id,
                "following_id": following_id,
                "action": action
            })
        elif action == "unfollow":
            self.social_graph[follower_id].discard(following_id)
            
            logger.info(f"{follower_id} unfollowed {following_id}", extra={
                "follower_id": follower_id,
                "following_id": following_id,
                "action": action
            })
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            **self.stats,
            "feed_pool_size": len(self.feed_pool),
            "agent_count": len(self.agent_pool),
            "social_graph_size": sum(len(following) for following in self.social_graph.values()),
            "total_actions_recorded": sum(len(actions) for actions in self.agent_actions.values()),
        }
    
    def _get_candidate_feeds(self, agent_id: str, context: Dict[str, Any]) -> List[Any]:
        """Get candidate feeds for an agent."""
        # Get feeds from followed users
        following = self.social_graph.get(agent_id, set())
        
        if following:
            # Show feeds from followed users
            candidate_feeds = [
                feed for feed in self.feed_pool
                if getattr(feed, 'author_id', None) in following
            ]
        else:
            # No follows yet - show all feeds or recent popular
            candidate_feeds = self.feed_pool[-100:]  # Last 100 feeds
        
        return candidate_feeds
    
    def _get_agent_context(self, agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build agent context for ranking."""
        return {
            "agent_metadata": self.agent_pool.get(agent_id, {}),
            "following": list(self.social_graph.get(agent_id, set())),
            "history": self.feed_history.get(agent_id, []),
            "actions": self.agent_actions.get(agent_id, []),
            **context
        }
    
    def _suggest_users(self, agent_id: str, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Suggest users to follow."""
        following = self.social_graph.get(agent_id, set())
        
        # Friends of friends
        suggested = set()
        for following_id in following:
            suggested.update(self.social_graph.get(following_id, set()))
        
        # Remove already following and self
        suggested -= following
        suggested.discard(agent_id)
        
        # Return sample
        suggested_list = list(suggested)[:5]
        return [{"id": user_id} for user_id in suggested_list]
    
    def _get_trending_topics(self, context: Dict[str, Any]) -> List[str]:
        """Get trending topics from recent feeds."""
        # Extract hashtags from recent feeds
        hashtags = []
        recent_feeds = self.feed_pool[-100:]  # Last 100 feeds
        
        for feed in recent_feeds:
            text = getattr(feed, 'text', '')
            # Simple hashtag extraction
            words = text.split()
            feed_hashtags = [word for word in words if word.startswith('#')]
            hashtags.extend(feed_hashtags)
        
        # Count and return top trending
        if hashtags:
            hashtag_counts = Counter(hashtags)
            return [tag for tag, _ in hashtag_counts.most_common(5)]
        
        return []

