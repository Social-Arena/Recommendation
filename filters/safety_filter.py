"""
Safety Filter - Remove unsafe and low-quality content
"""

from typing import List, Dict, Any
import random

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.utils.logger import get_logger


class ToxicityDetector:
    """Detect toxic content"""
    
    def score(self, text: str) -> float:
        """Score toxicity (0-1)"""
        toxic_words = ["hate", "violence", "attack", "abuse", "kill"]
        text_lower = text.lower()
        
        toxicity = sum(1 for word in toxic_words if word in text_lower)
        return min(toxicity / len(toxic_words), 1.0)


class MisinformationDetector:
    """Detect misinformation"""
    
    def score(self, content: Dict[str, Any]) -> float:
        """Score misinformation risk (0-1)"""
        suspicious = ["fake", "hoax", "conspiracy", "false", "lie"]
        text = content.get("text", "").lower()
        
        score = sum(1 for word in suspicious if word in text)
        return min(score / len(suspicious), 1.0)


class SpamDetector:
    """Detect spam content"""
    
    def score(self, content: Dict[str, Any]) -> float:
        """Score spam likelihood (0-1)"""
        spam_indicators = ["click here", "buy now", "limited time", "act fast", "free money"]
        text = content.get("text", "").lower()
        
        score = sum(1 for indicator in spam_indicators if indicator in text)
        return min(score / len(spam_indicators), 1.0)


class NSFWDetector:
    """Detect NSFW content"""
    
    def score(self, content: Dict[str, Any]) -> float:
        """Score NSFW likelihood (0-1)"""
        # Mock detector
        return random.uniform(0.0, 0.1)


class SafetyFilter:
    """Safety filter - filters unsafe content"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("safety_filter")
        
        # Initialize detectors
        self.toxicity_detector = ToxicityDetector()
        self.misinfo_detector = MisinformationDetector()
        self.spam_detector = SpamDetector()
        self.nsfw_detector = NSFWDetector()
        
        # Thresholds
        self.thresholds = {
            "toxicity": 0.7,
            "misinformation": 0.7,
            "spam": 0.7,
            "nsfw": 0.8
        }
    
    async def filter(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter unsafe and low-quality content
        
        Args:
            candidates: Candidate content
            
        Returns:
            Filtered safe content
        """
        filtered = []
        removed_count = 0
        
        for content in candidates:
            # Assess safety
            safety_score = await self._assess_safety(content)
            
            if safety_score >= self.config.safety_threshold:
                content["safety_score"] = safety_score
                filtered.append(content)
            else:
                removed_count += 1
                self._log_filtered_content(content, safety_score)
        
        self.logger.info(f"Safety filtering complete", extra={
            "input_count": len(candidates),
            "output_count": len(filtered),
            "removed_count": removed_count
        })
        
        return filtered
    
    async def _assess_safety(self, content: Dict[str, Any]) -> float:
        """Assess content safety"""
        text = content.get("text", "")
        
        # Run all safety checks
        checks = {
            "toxicity": self.toxicity_detector.score(text),
            "misinformation": self.misinfo_detector.score(content),
            "spam": self.spam_detector.score(content),
            "nsfw": self.nsfw_detector.score(content)
        }
        
        # Calculate overall safety (1.0 = completely safe)
        safety = 1.0
        for check_type, score in checks.items():
            if score > self.thresholds[check_type]:
                # Penalize safety score
                safety *= (1 - score)
        
        return safety
    
    def _log_filtered_content(self, content: Dict[str, Any], safety_score: float) -> None:
        """Log filtered content"""
        self.logger.warning(f"Content filtered", extra={
            "content_id": content.get("id"),
            "safety_score": safety_score,
            "reason": "safety_threshold"
        })

