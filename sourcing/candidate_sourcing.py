"""
Candidate Sourcing - Generate candidate pool from multiple sources
"""

from typing import List, Dict, Any
from collections import defaultdict

from Recommendation.config.rec_config import RecommendationConfig
from Recommendation.sourcing.in_network_source import InNetworkSource
from Recommendation.sourcing.out_network_source import OutOfNetworkSource
from Recommendation.sourcing.social_proof_source import SocialProofSource
from Recommendation.utils.logger import get_logger


class CandidateSourcing:
    """Candidate sourcing - generates candidate pool"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.logger = get_logger("candidate_sourcing")
        
        # Initialize sources
        self.in_network_source = InNetworkSource(config)
        self.out_network_source = OutOfNetworkSource(config)
        self.social_proof_source = SocialProofSource(config)
    
    async def generate_candidates(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Generate candidate pool for user
        
        Args:
            user_id: User ID
            
        Returns:
            List of candidate content
        """
        # Calculate source sizes based on ratios
        in_network_size = int(self.config.candidate_pool_size * self.config.in_network_ratio)
        out_network_size = int(self.config.candidate_pool_size * self.config.out_network_ratio)
        social_proof_size = int(self.config.candidate_pool_size * self.config.social_proof_ratio)
        
        # Generate from each source
        in_network_candidates = await self.in_network_source.generate_candidates(user_id, in_network_size)
        out_network_candidates = await self.out_network_source.generate_candidates(user_id, out_network_size)
        social_proof_candidates = await self.social_proof_source.generate_candidates(user_id, social_proof_size)
        
        # Merge candidates
        all_candidates = in_network_candidates + out_network_candidates + social_proof_candidates
        
        # Deduplicate
        deduplicated = self._deduplicate(all_candidates)
        
        self.logger.info(f"Candidates generated", extra={
            "user_id": user_id,
            "in_network": len(in_network_candidates),
            "out_network": len(out_network_candidates),
            "social_proof": len(social_proof_candidates),
            "total": len(deduplicated)
        })
        
        return deduplicated[:self.config.candidate_pool_size]
    
    def _deduplicate(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate candidates"""
        seen = set()
        unique = []
        
        for candidate in candidates:
            content_id = candidate.get("id", "")
            if content_id and content_id not in seen:
                seen.add(content_id)
                unique.append(candidate)
        
        return unique

