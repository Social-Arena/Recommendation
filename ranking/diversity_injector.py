"""
Diversity Injector - Ensure diverse, non-repetitive feed
"""

from typing import List, Dict, Any, Set
from collections import defaultdict

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class DiversityInjector:
    """Diversity injector - ensures feed diversity"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("diversity_injector")
    
    async def inject_diversity(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Inject diversity constraints
        
        Args:
            ranked: Ranked content
            
        Returns:
            Diversified content list
        """
        diversified = []
        
        # Track diversity metrics
        topics_seen: Set[str] = set()
        authors_seen = defaultdict(int)
        content_texts: List[str] = []
        
        for content in ranked:
            # Check diversity constraints
            if self._meets_diversity_constraints(
                content,
                topics_seen,
                authors_seen,
                content_texts
            ):
                diversified.append(content)
                
                # Update tracking
                content_topics = content.get("topics", [])
                topics_seen.update(content_topics)
                
                author_id = content.get("author_id", "")
                authors_seen[author_id] += 1
                
                content_text = content.get("text", "")
                content_texts.append(content_text)
            
            # Stop if we have enough
            if len(diversified) >= 100:
                break
        
        self.logger.debug(f"Diversity injected", extra={
            "input_count": len(ranked),
            "output_count": len(diversified),
            "unique_topics": len(topics_seen),
            "unique_authors": len(authors_seen)
        })
        
        return diversified
    
    def _meets_diversity_constraints(
        self,
        content: Dict[str, Any],
        topics_seen: Set[str],
        authors_seen: Dict[str, int],
        content_texts: List[str]
    ) -> bool:
        """Check if content meets diversity constraints"""
        # Author diversity
        author_id = content.get("author_id", "")
        if authors_seen[author_id] >= self.config.max_same_author:
            return False
        
        # Topic diversity
        content_topics = set(content.get("topics", []))
        if content_topics:
            topic_overlap = len(content_topics & topics_seen) / len(content_topics)
            if topic_overlap > self.config.max_topic_repetition:
                return False
        
        # Content similarity (simple text-based)
        content_text = content.get("text", "")
        if self._is_too_similar(content_text, content_texts):
            return False
        
        return True
    
    def _is_too_similar(self, text: str, previous_texts: List[str]) -> bool:
        """Check if text is too similar to previous content"""
        if not previous_texts:
            return False
        
        # Simple similarity check - word overlap
        text_words = set(text.lower().split())
        
        for prev_text in previous_texts[-10:]:  # Check last 10
            prev_words = set(prev_text.lower().split())
            
            if not text_words or not prev_words:
                continue
            
            overlap = len(text_words & prev_words) / len(text_words | prev_words)
            if overlap > 0.7:  # 70% similarity threshold
                return True
        
        return False

