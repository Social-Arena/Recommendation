"""
Base classes and protocols for the recommendation system.
"""

from typing import Protocol, Dict, List, Any, Set
from datetime import datetime
from pydantic import BaseModel, Field


class RecommendationMetrics(BaseModel):
    """Metrics for evaluating recommendation system performance."""
    
    # Engagement metrics
    click_through_rate: float = 0.0
    time_spent: float = 0.0
    
    # Diversity metrics
    content_diversity: float = 0.0
    creator_diversity: float = 0.0
    
    # Network metrics
    network_density: float = 0.0
    information_flow: float = 0.0
    
    # Fairness metrics
    creator_visibility: Dict[str, float] = Field(default_factory=dict)
    filter_bubble_score: float = 0.0


class RecommendationSystem(Protocol):
    """
    Protocol that all recommendation systems must implement.
    
    This is the platform algorithm that controls information flow
    between agents and feeds in Social Arena.
    """
    
    def ingest_feed(self, feed: Any) -> None:
        """
        Add new content to the system.
        
        When any agent creates content (post/reply/retweet/quote),
        it enters the recommendation system's feed pool.
        
        Args:
            feed: Feed object to add to the pool
        """
        ...
    
    def fetch(self, agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return personalized content for a specific agent.
        
        This is THE core function - it implements the algorithm that
        determines what each agent sees.
        
        Args:
            agent_id: Which agent is requesting content
            context: Additional context (time, location, recent activity)
        
        Returns:
            Dictionary containing:
                - feeds: List[Feed] - Ranked/filtered posts to show
                - users: List[User] - Suggested users to follow
                - trends: List[str] - Trending topics/hashtags
                - metadata: Dict - Algorithm explanation (optional)
        """
        ...
    
    def record_action(
        self,
        agent_id: str,
        action: str,
        target_id: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Record agent action for learning and feedback.
        
        When agents like, reply, follow, etc., the system learns:
        - What content engages which agents
        - How to better personalize future feeds
        - Which creators to amplify
        
        Args:
            agent_id: Agent performing the action
            action: Type of action (like, reply, follow, etc.)
            target_id: Target of the action (feed_id, user_id, etc.)
            metadata: Additional action metadata
        """
        ...
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get system statistics for analysis.
        
        Returns:
            Dictionary with system statistics (feed count, agent count, etc.)
        """
        ...
    
    def add_agent(self, agent_id: str, metadata: Dict[str, Any] = None) -> None:
        """
        Register a new agent in the system.
        
        Args:
            agent_id: Unique agent identifier
            metadata: Agent metadata (interests, bio, etc.)
        """
        ...
    
    def update_social_graph(self, follower_id: str, following_id: str, action: str = "follow") -> None:
        """
        Update the social graph when agents follow/unfollow.
        
        Args:
            follower_id: Agent doing the following
            following_id: Agent being followed
            action: "follow" or "unfollow"
        """
        ...


class RecommendationStrategy(Protocol):
    """
    Protocol for recommendation strategies.
    
    Different strategies implement different algorithms for ranking
    and filtering content.
    """
    
    def rank_feeds(
        self,
        feeds: List[Any],
        agent_id: str,
        context: Dict[str, Any]
    ) -> List[Any]:
        """
        Rank feeds for a specific agent.
        
        Args:
            feeds: List of candidate feeds
            agent_id: Target agent
            context: Additional context
        
        Returns:
            Ranked list of feeds
        """
        ...

