# Recommendation - Twitter-Inspired Recommendation Engine 🎯

**7-Step Recommendation Pipeline with Dual-Tower Architecture**

The Recommendation module implements Twitter's recommendation algorithm, featuring candidate generation, multi-task ranking, exploration engines, diversity injection, and real-time serving infrastructure.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [7-Step Pipeline](#7-step-pipeline)
- [Directory Structure](#directory-structure)
- [Core Components](#core-components)
- [Dual-Tower Model](#dual-tower-model)
- [Exploration Strategies](#exploration-strategies)
- [A/B Testing Framework](#ab-testing-framework)
- [Integration](#integration)
- [Configuration](#configuration)
- [Development Guide](#development-guide)

---

## 🎯 Overview

The Recommendation Engine is designed to replicate Twitter's state-of-the-art recommendation system, providing personalized content feeds for agents in the simulation.

### ✅ Currently Implemented

- ✅ **7-Step Recommendation Pipeline**: Fully functional end-to-end pipeline
- ✅ **Candidate Sourcing**: In-Network (40%), Out-of-Network (50%), Social Proof (10%)
- ✅ **Light Ranking**: Fast feature extraction with top-500 selection
- ✅ **Heavy Ranking**: Multi-task model interface with utility scoring
- ✅ **Exploration Engine**: ε-greedy, UCB, Thompson Sampling (all 3 strategies)
- ✅ **Diversity Injection**: Topic, author, and content similarity constraints
- ✅ **Safety Filtering**: Toxicity, misinformation, spam, NSFW detection
- ✅ **Real-time Serving**: Caching, metrics tracking, < 100ms target latency
- ✅ **Trace Logging**: Complete file-based logging with request tracing

### 🚧 In Development / Planned

- 🚧 **Dual-Tower Neural Network**: Currently using mock predictions (interface ready)
- 🚧 **A/B Testing Framework**: Config parameters exist, framework not built
- 🚧 **Monitoring Dashboards**: Log infrastructure exists, dashboards not built
- 🚧 **Online Learning**: Model update pipeline not yet implemented

### Key Features

- **7-Step Pipeline**: Candidate Sourcing → Light Ranking → Heavy Ranking → Exploration → Diversity → Safety → Serving
- **Multiple Exploration Strategies**: ε-greedy (ε=0.1), UCB (c=2.0), Thompson Sampling
- **Diversity Constraints**: Max 2 posts per author, 30% topic overlap limit, 70% similarity threshold
- **Safety Thresholds**: Toxicity (0.7), Misinformation (0.7), Spam (0.7), NSFW (0.8)
- **Performance**: Target < 100ms latency, 5-minute cache TTL
- **File-based Logging**: All components log to `trace/recommendation/*.log`

### Reference

Implementation based on: https://github.com/twitter/the-algorithm

---

## 🏗️ System Architecture

```
Recommendation Engine
┌─────────────────────────────────────────────────────────────┐
│                     Candidate Sourcing                       │
│─────────────────────────────────────────────────────────────│
│  In-Network Source      Out-of-Network Source   Social Proof │
│  (Following authors)     (Interest clusters)    (Friend acts)│
│  generate_candidates()  generate_candidates()   generate()   │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Candidate Pool / Deduplication             │
│  - Merge candidates from all sources                         │
│  - Deduplicate / Filter already seen / Basic safety         │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        Light Ranking                         │
│─────────────────────────────────────────────────────────────│
│  Light Feature Extraction                                     │
│  - Content features: age, engagement velocity, author stats  │
│  - User matching: interests, historical patterns             │
│  Light Score / Combined Score                                 │
│  Output top candidates to heavy ranking                       │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        Heavy Ranking                         │
│─────────────────────────────────────────────────────────────│
│  Multi-Task Model                                             │
│  - Predict: like/retweet/reply/click/dwell time/negative    │
│  Utility Scorer                                               │
│  - Combine multi-task predictions with personalization       │
│  Output final utility scores                                  │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       Exploration Engine                     │
│─────────────────────────────────────────────────────────────│
│  ε-greedy / UCB / Thompson Sampling                           │
│  - Give new content opportunities                             │
│  - Adjust ranking with exploration bonus                      │
│  Output exploration-adjusted candidates                       │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Diversity & Safety                       │
│─────────────────────────────────────────────────────────────│
│  - Topic diversity / Author diversity / Content similarity   │
│  - Violation filtering                                        │
│  Output final diversified, safe ranking                       │
└─────────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                        User Feed / Agent                      │
│  - Audience Agent receives recommendations                    │
│  - Interaction behavior feeds back, drives learning updates  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Directory Structure

```
Recommendation/
│
├── config/                        # Configuration
│   ├── __init__.py
│   └── rec_config.py             # RecommendationConfig dataclass
│
├── core/                          # Core engine
│   ├── __init__.py
│   └── recommendation_engine.py  # RecommendationEngine, RecommendationResponse
│
├── sourcing/                      # Candidate sources (Step 1)
│   ├── __init__.py
│   ├── candidate_sourcing.py     # CandidateSourcing orchestrator
│   ├── in_network_source.py      # InNetworkSource - content from followed authors
│   ├── out_network_source.py     # OutOfNetworkSource - interest clusters, trending, similar users
│   └── social_proof_source.py    # SocialProofSource - friend engagement signals
│
├── ranking/                       # Ranking systems (Steps 2-4)
│   ├── __init__.py
│   ├── light_ranker.py           # LightRanker - fast lightweight features
│   ├── heavy_ranker.py           # HeavyRanker, MultiTaskModel, UtilityScorer
│   ├── exploration_engine.py     # ExplorationEngine - ε-greedy, UCB, Thompson Sampling
│   └── diversity_injector.py     # DiversityInjector - topic/author/content diversity
│
├── filters/                       # Filtering systems (Step 6)
│   ├── __init__.py
│   └── safety_filter.py          # SafetyFilter + all detector classes:
│                                  #   ToxicityDetector, MisinformationDetector,
│                                  #   SpamDetector, NSFWDetector
│
├── utils/                         # Utilities & infrastructure
│   ├── __init__.py
│   ├── logger.py                 # get_logger() - file-based trace logging
│   ├── decorators.py             # @log_performance, @log_errors, @trace_execution
│   ├── trace_request.py          # RequestTracer - pipeline flow tracing
│   └── log_analyzer.py           # LogAnalyzer - metrics & analysis
│
├── trace/                         # Trace logging storage
│   ├── recommendation/           # Component-specific log files
│   │   ├── recommendation_engine.log
│   │   ├── candidate_sourcing.log
│   │   ├── in_network_source.log
│   │   ├── out_network_source.log
│   │   ├── social_proof_source.log
│   │   ├── light_ranker.log
│   │   ├── heavy_ranker.log
│   │   ├── exploration_engine.log
│   │   ├── diversity_injector.log
│   │   └── safety_filter.log
│   └── logs/                     # Additional log categories
│       ├── ab_test/
│       ├── candidate/
│       ├── diversity/
│       ├── errors/
│       ├── exploration/
│       ├── performance/
│       └── ranking/
│
├── examples/                      # Example usage
│   ├── __init__.py
│   ├── recommendation_example.py # Complete pipeline example
│   └── logging_example.py        # Logging system demonstration
│
├── __init__.py                    # Package initialization
├── test_logging.py               # Logging system test
├── Structure.mermaid             # System architecture diagram
├── README.md                     # This file
├── LOGGING_SYSTEM.md             # Logging documentation
└── LICENSE                       # License file
```

### Implementation Status

✅ **Fully Implemented**:
- 7-step recommendation pipeline
- All candidate sourcing (In-Network, Out-of-Network, Social Proof)
- Light ranking with feature extraction
- Heavy ranking with multi-task model (mock predictions)
- Exploration strategies (ε-greedy, UCB, Thompson Sampling)
- Diversity injection (topic, author, content similarity)
- Safety filtering (toxicity, misinformation, spam, NSFW detection)
- File-based trace logging infrastructure
- Request tracing and log analysis

🚧 **Planned/Future**:
- Dual-tower neural network model (currently using mock predictions)
- Real-time serving infrastructure (feed mixer, A/B testing framework)
- Monitoring dashboards (metrics, bias detection)
- Comprehensive test suite

---

## 🔄 7-Step Pipeline

### Step 1: Candidate Sourcing

**Goal**: Generate a candidate pool of ~1500 content items per user

**Implementation**: `sourcing/candidate_sourcing.py`

```python
class CandidateSourcing:
    """Generate candidate pool from multiple sources"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.in_network_source = InNetworkSource(config)
        self.out_network_source = OutOfNetworkSource(config)
        self.social_proof_source = SocialProofSource(config)
    
    async def generate_candidates(self, user_id: str) -> List[Dict[str, Any]]:
        # Calculate source sizes based on ratios
        in_network_size = int(self.config.candidate_pool_size * self.config.in_network_ratio)
        out_network_size = int(self.config.candidate_pool_size * self.config.out_network_ratio)
        social_proof_size = int(self.config.candidate_pool_size * self.config.social_proof_ratio)
        
        # Generate from each source
        in_network = await self.in_network_source.generate_candidates(user_id, in_network_size)
        out_network = await self.out_network_source.generate_candidates(user_id, out_network_size)
        social_proof = await self.social_proof_source.generate_candidates(user_id, social_proof_size)
        
        # Merge and deduplicate
        all_candidates = in_network + out_network + social_proof
        deduplicated = self._deduplicate(all_candidates)
        
        return deduplicated[:self.config.candidate_pool_size]
```

**Key Sources**:
- **In-Network** (`in_network_source.py`) - 40%: Content from followed authors
- **Out-of-Network** (`out_network_source.py`) - 50%: Interest-based (60%), Trending (30%), Similar users (10%)
- **Social Proof** (`social_proof_source.py`) - 10%: Content friends engaged with

---

### Step 2: Light Ranking

**Goal**: Fast initial ranking to reduce candidate pool

**Implementation**: `ranking/light_ranker.py`

```python
class LightRanker:
    """Fast ranking with lightweight features"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
    
    async def rank(self, candidates: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        ranked = []
        
        for candidate in candidates:
            # Extract lightweight features
            features = self._extract_light_features(candidate, user_id)
            
            # Compute light score
            score = self._compute_light_score(features)
            
            # Add score to candidate
            candidate["light_score"] = score
            ranked.append(candidate)
        
        # Sort by light score and return top K
        ranked.sort(key=lambda x: x["light_score"], reverse=True)
        return ranked[:self.config.light_ranking_top_k]
    
    def _compute_light_score(self, features: Dict[str, float]) -> float:
        """Weighted combination of lightweight features"""
        score = (
            features["age_score"] * 0.2 +           # Content freshness
            features["velocity_score"] * 0.3 +       # Engagement rate
            features["influence_score"] * 0.2 +      # Author influence
            features["match_score"] * 0.3            # User-content match
        )
        return score
```

**Light Features** (fast to compute):
- **Content age**: Freshness score (1 - hours_old / 48)
- **Engagement velocity**: likes/shares per hour normalized
- **Author influence**: Follower count normalized
- **User-content match**: Historical interaction patterns

---

### Step 3: Heavy Ranking (Multi-Task)

**Goal**: Precise ranking with multi-task predictions

**Implementation**: `ranking/heavy_ranker.py`

```python
class HeavyRanker:
    """Heavy ranking with multi-task model"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.multi_task_model = MultiTaskModel()
        self.utility_scorer = UtilityScorer()
    
    async def rank(self, candidates: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        ranked = []
        
        # Get user preferences
        user_preferences = self._get_user_preferences(user_id)
        
        for candidate in candidates:
            # Extract deep features (embeddings, detailed stats)
            features = self._extract_deep_features(candidate, user_id)
            
            # Multi-task predictions
            predictions = self.multi_task_model.predict(features)
            
            # Compute utility score
            utility = self.utility_scorer.score(predictions, user_preferences)
            
            # Add to candidate
            candidate["predictions"] = predictions
            candidate["utility"] = utility
            ranked.append(candidate)
        
        # Sort by utility and return top K
        ranked.sort(key=lambda x: x["utility"], reverse=True)
        return ranked[:self.config.heavy_ranking_top_k]
```

**Multi-Task Predictions**:
- **p_like**: Probability of like (0.1 - 0.9)
- **p_retweet**: Probability of retweet (0.05 - 0.5)
- **p_reply**: Probability of reply (0.02 - 0.3)
- **p_click**: Probability of click (0.1 - 0.7)
- **expected_dwell_time**: Expected viewing time in seconds (1.0 - 30.0)
- **p_negative**: Probability of negative feedback (0.01 - 0.1)

**Utility Function** (UtilityScorer):
```python
utility = (
    w_like * P(like)              +  # Weight: 1.0
    w_retweet * P(retweet)        +  # Weight: 2.0
    w_reply * P(reply)            +  # Weight: 3.0
    w_click * P(click)            +  # Weight: 1.5
    w_dwell * E(dwell_time)       +  # Weight: 0.1
    w_negative * P(negative)         # Weight: -5.0 (penalty)
)
```

*Note: Currently uses mock predictions for development. Production will use trained neural network.*

---

### Step 4: Exploration Engine

**Goal**: Balance exploitation and exploration

**Implementation**: `ranking/exploration_engine.py`

```python
class ExplorationEngine:
    """Exploration strategies for discovery"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        self.content_stats = {}  # Track impressions and rewards
        self.total_impressions = 0
    
    async def apply_exploration(self, ranked: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        strategy = self.config.exploration_strategy
        
        if strategy == "epsilon_greedy":
            result = self._epsilon_greedy(ranked)
        elif strategy == "ucb":
            result = self._ucb(ranked)
        elif strategy == "thompson_sampling":
            result = self._thompson_sampling(ranked)
        else:
            result = ranked
        
        return result
    
    def _epsilon_greedy(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ε-greedy: Randomly boost content with probability ε"""
        explored = ranked.copy()
        
        for i in range(len(explored)):
            if random.random() < self.config.epsilon:
                # Add exploration bonus
                explored[i]["utility"] = explored[i].get("utility", 0.5) + random.uniform(0.1, 0.5)
        
        # Re-sort by adjusted utility
        explored.sort(key=lambda x: x.get("utility", 0), reverse=True)
        return explored
    
    def _ucb(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Upper Confidence Bound: UCB = mean_reward + c * sqrt(ln(N) / n)"""
        explored = []
        
        for content in ranked:
            content_id = content.get("id", "")
            
            # Get historical stats
            if content_id not in self.content_stats:
                self.content_stats[content_id] = {"impressions": 0, "total_reward": 0.0}
            
            stats = self.content_stats[content_id]
            
            # Calculate UCB score
            if stats["impressions"] == 0:
                ucb_score = float('inf')  # Always try new content first
            else:
                mean_reward = stats["total_reward"] / stats["impressions"]
                exploration_bonus = self.config.ucb_confidence * math.sqrt(
                    math.log(self.total_impressions + 1) / stats["impressions"]
                )
                ucb_score = mean_reward + exploration_bonus
            
            content["ucb_score"] = ucb_score
            content["utility"] = ucb_score
            explored.append(content)
        
        # Sort by UCB score
        explored.sort(key=lambda x: x.get("ucb_score", 0), reverse=True)
        return explored
    
    def _thompson_sampling(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Thompson Sampling: Sample from Beta(successes, failures) distribution"""
        import numpy as np
        
        explored = []
        
        for content in ranked:
            content_id = content.get("id", "")
            
            # Get stats (Beta distribution parameters)
            if content_id not in self.content_stats:
                self.content_stats[content_id] = {"successes": 1, "failures": 1}
            
            stats = self.content_stats[content_id]
            
            # Sample from Beta distribution
            sample = np.random.beta(stats["successes"], stats["failures"])
            
            content["thompson_sample"] = sample
            content["utility"] = sample
            explored.append(content)
        
        # Sort by sampled value
        explored.sort(key=lambda x: x.get("thompson_sample", 0), reverse=True)
        return explored
    
    def record_impression(self, content_id: str, engagement: bool, reward: float = 0.0) -> None:
        """Record impression for learning"""
        if content_id not in self.content_stats:
            self.content_stats[content_id] = {
                "impressions": 0, "total_reward": 0.0,
                "successes": 1, "failures": 1
            }
        
        stats = self.content_stats[content_id]
        stats["impressions"] += 1
        stats["total_reward"] += reward
        
        if engagement:
            stats["successes"] += 1
        else:
            stats["failures"] += 1
        
        self.total_impressions += 1
```

**Strategies Implemented**:
- **ε-greedy** (epsilon=0.1): Random exploration with probability ε
- **UCB** (confidence=2.0): Upper Confidence Bound with systematic exploration bonus
- **Thompson Sampling**: Bayesian approach with Beta distribution sampling

---

### Step 5: Diversity Injection

**Goal**: Ensure diverse, non-repetitive feed

**Implementation**: `ranking/diversity_injector.py`

```python
class DiversityInjector:
    """Inject diversity constraints"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
    
    async def inject_diversity(self, ranked: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        diversified = []
        
        # Track diversity metrics
        topics_seen: Set[str] = set()
        authors_seen = defaultdict(int)
        content_texts: List[str] = []
        
        for content in ranked:
            # Check diversity constraints
            if self._meets_diversity_constraints(
                content, topics_seen, authors_seen, content_texts
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
        
        return diversified
    
    def _meets_diversity_constraints(
        self,
        content: Dict[str, Any],
        topics_seen: Set[str],
        authors_seen: Dict[str, int],
        content_texts: List[str]
    ) -> bool:
        """Check if content meets diversity constraints"""
        
        # 1. Author diversity - max 2 posts from same author
        author_id = content.get("author_id", "")
        if authors_seen[author_id] >= self.config.max_same_author:
            return False
        
        # 2. Topic diversity - limit topic repetition to 30%
        content_topics = set(content.get("topics", []))
        if content_topics:
            topic_overlap = len(content_topics & topics_seen) / len(content_topics)
            if topic_overlap > self.config.max_topic_repetition:
                return False
        
        # 3. Content similarity - check text similarity (Jaccard)
        content_text = content.get("text", "")
        if self._is_too_similar(content_text, content_texts):
            return False
        
        return True
    
    def _is_too_similar(self, text: str, previous_texts: List[str]) -> bool:
        """Check if text is too similar to previous content"""
        if not previous_texts:
            return False
        
        # Simple word-based Jaccard similarity
        text_words = set(text.lower().split())
        
        # Check last 10 posts for similarity
        for prev_text in previous_texts[-10:]:
            prev_words = set(prev_text.lower().split())
            
            if not text_words or not prev_words:
                continue
            
            # Jaccard similarity: |A ∩ B| / |A ∪ B|
            overlap = len(text_words & prev_words) / len(text_words | prev_words)
            if overlap > 0.7:  # 70% similarity threshold
                return True
        
        return False
```

**Diversity Dimensions Implemented**:
- **Topic Diversity**: Max 30% topic overlap with seen topics
- **Author Diversity**: Max 2 posts from same author
- **Content Similarity**: Max 70% Jaccard similarity with recent content

**Config Parameters**:
```python
max_same_author: int = 2              # Max posts per author
max_topic_repetition: float = 0.3     # Max topic overlap (30%)
min_topic_diversity: int = 5          # Minimum unique topics
```

---

### Step 6: Safety Filtering

**Goal**: Remove unsafe, low-quality content

**Implementation**: `filters/safety_filter.py`

```python
class SafetyFilter:
    """Filter unsafe and low-quality content"""
    
    def __init__(self, config: RecommendationConfig):
        self.config = config
        
        # Initialize detectors
        self.toxicity_detector = ToxicityDetector()
        self.misinfo_detector = MisinformationDetector()
        self.spam_detector = SpamDetector()
        self.nsfw_detector = NSFWDetector()
        
        # Thresholds for each detector
        self.thresholds = {
            "toxicity": 0.7,
            "misinformation": 0.7,
            "spam": 0.7,
            "nsfw": 0.8
        }
    
    async def filter(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter unsafe and low-quality content"""
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
        
        return filtered
    
    async def _assess_safety(self, content: Dict[str, Any]) -> float:
        """Assess content safety (1.0 = completely safe)"""
        text = content.get("text", "")
        
        # Run all safety checks
        checks = {
            "toxicity": self.toxicity_detector.score(text),
            "misinformation": self.misinfo_detector.score(content),
            "spam": self.spam_detector.score(content),
            "nsfw": self.nsfw_detector.score(content)
        }
        
        # Calculate overall safety: safety = 1.0 * Π(1 - score_i) for violations
        safety = 1.0
        for check_type, score in checks.items():
            if score > self.thresholds[check_type]:
                # Penalize safety score
                safety *= (1 - score)
        
        return safety
```

**Safety Detectors** (all in `safety_filter.py`):

1. **ToxicityDetector**: Detects hate speech, violence, abuse
   - Checks for toxic keywords
   - Threshold: 0.7

2. **MisinformationDetector**: Detects fake news, conspiracy theories
   - Checks for suspicious patterns
   - Threshold: 0.7

3. **SpamDetector**: Detects spam, promotional content
   - Checks for spam indicators (buy now, click here, etc.)
   - Threshold: 0.7

4. **NSFWDetector**: Detects adult/NSFW content
   - Mock detector (returns low risk scores)
   - Threshold: 0.8

**Overall Safety Score**:
```python
# Content passes if: safety_score >= config.safety_threshold (0.7)
safety = 1.0
for detector_score in [toxicity, misinfo, spam, nsfw]:
    if detector_score > threshold:
        safety *= (1 - detector_score)
```

---

### Step 7: Real-time Serving

**Goal**: Serve recommendations with < 100ms latency

**Implementation**: `core/recommendation_engine.py`

```python
class RecommendationEngine:
    """Main recommendation engine orchestrating 7-step pipeline"""
    
    def __init__(self, config: Optional[RecommendationConfig] = None):
        self.config = config or RecommendationConfig()
        
        # Initialize pipeline components
        self.candidate_sourcing = CandidateSourcing(self.config)
        self.light_ranker = LightRanker(self.config)
        self.heavy_ranker = HeavyRanker(self.config)
        self.exploration_engine = ExplorationEngine(self.config)
        self.diversity_injector = DiversityInjector(self.config)
        self.safety_filter = SafetyFilter(self.config)
        
        # Cache for recommendations
        self.cache: Dict[str, Any] = {}
        
        # Metrics
        self.request_count = 0
        self.total_latency = 0.0
    
    async def recommend(
        self,
        user_id: str,
        num_results: int = 100,
        context: Optional[Dict[str, Any]] = None
    ) -> RecommendationResponse:
        """Generate recommendations for user"""
        start_time = time.time()
        
        # Check cache
        cache_key = f"{user_id}:{num_results}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if time.time() - cached["timestamp"] < self.config.cache_ttl:
                return RecommendationResponse(
                    recommendations=cached["recommendations"],
                    latency=time.time() - start_time,
                    metadata={"cached": True}
                )
        
        # Step 1: Candidate Sourcing (~1500 candidates)
        candidates = await self.candidate_sourcing.generate_candidates(user_id)
        
        # Step 2: Light Ranking (Top 500)
        light_ranked = await self.light_ranker.rank(candidates, user_id)
        
        # Step 3: Heavy Ranking (Top 100)
        heavy_ranked = await self.heavy_ranker.rank(light_ranked, user_id)
        
        # Step 4: Exploration
        explored = await self.exploration_engine.apply_exploration(heavy_ranked, user_id)
        
        # Step 5: Diversity Injection
        diversified = await self.diversity_injector.inject_diversity(explored)
        
        # Step 6: Safety Filtering
        filtered = await self.safety_filter.filter(diversified)
        
        # Step 7: Final results
        final_recommendations = filtered[:num_results]
        
        latency = time.time() - start_time
        
        # Update metrics
        self.request_count += 1
        self.total_latency += latency
        
        # Cache results (TTL: 300s)
        self.cache[cache_key] = {
            "recommendations": final_recommendations,
            "timestamp": time.time()
        }
        
        return RecommendationResponse(
            recommendations=final_recommendations,
            latency=latency,
            metadata={
                "cached": False,
                "pipeline_steps": 7,
                "candidate_count": len(candidates),
                "filtered_count": len(diversified) - len(filtered)
            }
        )

class RecommendationResponse:
    """Recommendation response"""
    
    def __init__(self, recommendations: List[Any], latency: float, metadata: Dict[str, Any]):
        self.recommendations = recommendations
        self.latency = latency
        self.metadata = metadata
```

**Performance Characteristics**:
- **Target Latency**: < 100ms
- **Cache TTL**: 300 seconds (5 minutes)
- **Cache Strategy**: Dict-based in-memory cache (key: user_id:num_results)
- **Metrics Tracked**: Total requests, average latency, cache size

---

## 🏛️ Multi-Task Model Architecture

### Current Implementation

The system currently uses a **MultiTaskModel** class (in `ranking/heavy_ranker.py`) that provides the interface for multi-task predictions:

```python
class MultiTaskModel:
    """Multi-task prediction model"""
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, float]:
        """
        Predict multiple engagement probabilities
        
        Returns:
            Dictionary of predictions:
            - p_like: Probability of like
            - p_retweet: Probability of retweet
            - p_reply: Probability of reply
            - p_click: Probability of click
            - expected_dwell_time: Expected time spent
            - p_negative: Probability of negative feedback
        """
        # Currently uses mock predictions for development/testing
        # Production: Replace with trained neural network
        return {
            "p_like": random.uniform(0.1, 0.9),
            "p_retweet": random.uniform(0.05, 0.5),
            "p_reply": random.uniform(0.02, 0.3),
            "p_click": random.uniform(0.1, 0.7),
            "expected_dwell_time": random.uniform(1.0, 30.0),
            "p_negative": random.uniform(0.01, 0.1)
        }
```

### UtilityScorer

```python
class UtilityScorer:
    """Compute utility score from multi-task predictions"""
    
    def score(self, predictions: Dict[str, float], user_preferences: Dict[str, float]) -> float:
        """
        Compute utility score with personalized weights
        
        utility = w_like * P(like) + w_rt * P(retweet) + w_reply * P(reply) 
                + w_click * P(click) + w_dwell * E(dwell_time) - w_neg * P(negative)
        """
        weights = {
            "like": 1.0,
            "retweet": 2.0,
            "reply": 3.0,
            "click": 1.5,
            "dwell_time": 0.1,
            "negative": -5.0
        }
        
        # Override with user preferences if available
        if user_preferences:
            weights.update(user_preferences)
        
        utility = (
            predictions["p_like"] * weights["like"] +
            predictions["p_retweet"] * weights["retweet"] +
            predictions["p_reply"] * weights["reply"] +
            predictions["p_click"] * weights["click"] +
            predictions["expected_dwell_time"] * weights["dwell_time"] +
            predictions["p_negative"] * weights["negative"]
        )
        
        return utility
```

### 🚧 Future: Dual-Tower Neural Network

**Planned Architecture** (not yet implemented):

```
User Tower                              Content Tower
    │                                       │
    ├─ User ID Embedding                    ├─ Content ID Embedding
    ├─ User Features                        ├─ Content Features
    │  - Demographics                       │  - Text embedding
    │  - Historical engagement              │  - Author features
    │  - Interest profile                   │  - Topic distribution
    │  - Network features                   │  - Engagement stats
    │                                       │
    ├─ Dense Layers                         ├─ Dense Layers
    │  (512 → 256 → 128)                    │  (512 → 256 → 128)
    │                                       │
    └──────────► User Embedding ────────────┴─► Dot Product → Similarity Score
                    (128-dim)                      Content Embedding
                                                      (128-dim)
```

**Benefits** (when implemented):
- Efficient candidate retrieval
- Scalable to millions of users/content
- Pre-compute content embeddings
- Fast online serving

---

## 🎲 Exploration Strategies

### 1. ε-Greedy

```python
def epsilon_greedy_select(ranked_items, epsilon=0.1):
    if random.random() < epsilon:
        return random.choice(ranked_items)  # Explore
    else:
        return ranked_items[0]  # Exploit best
```

### 2. Upper Confidence Bound (UCB)

```python
def ucb_score(item, total_impressions):
    mean_reward = item.total_reward / max(item.impressions, 1)
    exploration_bonus = math.sqrt(2 * math.log(total_impressions) / max(item.impressions, 1))
    return mean_reward + exploration_bonus
```

### 3. Thompson Sampling

```python
def thompson_sampling_select(items):
    samples = []
    for item in items:
        # Sample from Beta distribution
        alpha = item.successes + 1
        beta = item.failures + 1
        sample = np.random.beta(alpha, beta)
        samples.append((sample, item))
    
    return max(samples, key=lambda x: x[0])[1]
```

---

## 🧪 A/B Testing Framework

### Configuration Support

The `RecommendationConfig` includes A/B testing parameters:

```python
@dataclass
class RecommendationConfig:
    # A/B testing
    enable_ab_testing: bool = True
    default_experiment_duration: int = 7  # days
```

### 🚧 Future: Full A/B Testing Infrastructure

**Planned implementation** (not yet built):

```python
class ABTestFramework:
    """A/B testing for recommendation strategies"""
    
    def create_experiment(self, config: ExperimentConfig) -> Experiment:
        """Create new A/B test experiment"""
        experiment = Experiment(
            name=config.name,
            control_strategy=config.control_strategy,
            treatment_strategy=config.treatment_strategy,
            split_ratio=config.split_ratio,
            duration=config.duration
        )
        return experiment
    
    async def assign_user_to_group(self, user_id: str, experiment: Experiment) -> str:
        """Assign user to control or treatment group"""
        # Consistent hashing for stable assignment
        hash_value = hashlib.md5(f"{user_id}{experiment.id}".encode()).hexdigest()
        hash_int = int(hash_value, 16)
        
        if (hash_int % 100) < (experiment.split_ratio * 100):
            return "treatment"
        else:
            return "control"
    
    async def collect_metrics(self, experiment: Experiment) -> ExperimentMetrics:
        """Collect experiment metrics"""
        control_metrics = self._get_group_metrics(experiment, "control")
        treatment_metrics = self._get_group_metrics(experiment, "treatment")
        
        return ExperimentMetrics(
            control=control_metrics,
            treatment=treatment_metrics,
            p_value=self._calculate_p_value(control_metrics, treatment_metrics),
            effect_size=self._calculate_effect_size(control_metrics, treatment_metrics)
        )
```

**Use cases** (when implemented):
- Compare exploration strategies (ε-greedy vs UCB vs Thompson Sampling)
- Test different ranking weights
- Evaluate safety threshold adjustments
- Measure impact of diversity constraints

---

## 🔌 Integration

### With Arena System

```python
# Arena requests recommendations for agents
async def get_agent_recommendations(agent_id: str) -> List[Feed]:
    recommendations = await recommendation_api.get_recommendations(
        user_id=agent_id,
        context=arena.get_agent_context(agent_id)
    )
    return recommendations.recommendations
```

### With Feed System

```python
# Get content for recommendation
async def get_candidate_content() -> List[Feed]:
    # Get recent feeds
    feeds = await feed_manager.load_all_feeds()
    
    # Filter and prepare for recommendation
    candidates = prepare_candidates(feeds)
    return candidates
```

### With Agent System

```python
# Agent provides feedback
async def record_agent_interaction(agent_id: str, content_id: str, interaction: Interaction):
    await feedback_collector.record(
        user_id=agent_id,
        content_id=content_id,
        interaction_type=interaction.type,
        dwell_time=interaction.dwell_time
    )
```

---

## ⚙️ Configuration

**Location**: `config/rec_config.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
from Recommendation.config.rec_config import RecommendationConfig

@dataclass
class RecommendationConfig:
    """Configuration for recommendation engine"""
    
    # Candidate sourcing
    candidate_pool_size: int = 1500
    in_network_ratio: float = 0.4      # 40% from followed authors
    out_network_ratio: float = 0.5     # 50% from discovery
    social_proof_ratio: float = 0.1    # 10% from friend signals
    
    # Ranking
    light_ranking_top_k: int = 500     # Light ranker output size
    heavy_ranking_top_k: int = 100     # Heavy ranker output size
    
    # Exploration
    exploration_strategy: str = "epsilon_greedy"  # epsilon_greedy, ucb, thompson_sampling
    epsilon: float = 0.1               # ε-greedy exploration rate
    ucb_confidence: float = 2.0        # UCB confidence parameter
    
    # Diversity
    max_same_author: int = 2           # Max posts per author
    max_topic_repetition: float = 0.3  # Max topic overlap (30%)
    min_topic_diversity: int = 5       # Min unique topics
    
    # Safety
    safety_threshold: float = 0.7      # Overall safety threshold
    enable_toxicity_filter: bool = True
    enable_spam_filter: bool = True
    
    # Serving
    cache_ttl: int = 300               # Cache TTL in seconds (5 min)
    target_latency_ms: int = 100       # Target latency in milliseconds
    
    # A/B testing (planned)
    enable_ab_testing: bool = True
    default_experiment_duration: int = 7  # days
    
    # Model configuration (for future neural network)
    user_embedding_dim: int = 128
    content_embedding_dim: int = 128
    hidden_dim: int = 256
    
    # Trace logging
    log_level: str = "INFO"
    trace_dir: Path = field(default_factory=lambda: Path("trace"))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "candidate_pool_size": self.candidate_pool_size,
            "in_network_ratio": self.in_network_ratio,
            "out_network_ratio": self.out_network_ratio,
            "social_proof_ratio": self.social_proof_ratio,
            "light_ranking_top_k": self.light_ranking_top_k,
            "heavy_ranking_top_k": self.heavy_ranking_top_k,
            "exploration_strategy": self.exploration_strategy,
            "epsilon": self.epsilon,
            "ucb_confidence": self.ucb_confidence,
            "max_same_author": self.max_same_author,
            "max_topic_repetition": self.max_topic_repetition,
            "min_topic_diversity": self.min_topic_diversity,
            "safety_threshold": self.safety_threshold,
            "enable_toxicity_filter": self.enable_toxicity_filter,
            "enable_spam_filter": self.enable_spam_filter,
            "cache_ttl": self.cache_ttl,
            "target_latency_ms": self.target_latency_ms,
            "enable_ab_testing": self.enable_ab_testing,
            "default_experiment_duration": self.default_experiment_duration
        }


# Usage Example
config = RecommendationConfig()  # Uses all defaults

# Or customize
config = RecommendationConfig(
    candidate_pool_size=2000,
    exploration_strategy="ucb",
    safety_threshold=0.8
)
```

---

## 🛠️ Development Guide

### Development Status

#### Phase 1: Candidate Sourcing ✅ COMPLETE
1. ✅ In-Network source
2. ✅ Out-of-Network source (interest-based, trending, similar users)
3. ✅ Social Proof source
4. ✅ Candidate deduplication

#### Phase 2: Ranking Systems ✅ COMPLETE
1. ✅ Light Ranker with lightweight features
2. ✅ Heavy Ranker with multi-task model interface
3. ✅ Utility Scorer with weighted predictions
4. 🚧 Train dual-tower neural network (using mock predictions currently)

#### Phase 3: Exploration & Diversity ✅ COMPLETE
1. ✅ Exploration strategies (ε-greedy, UCB, Thompson Sampling)
2. ✅ Diversity injector (topic, author, content similarity)
3. ✅ Safety filters (toxicity, misinformation, spam, NSFW)
4. ✅ Serving pipeline with caching

#### Phase 4: A/B Testing & Monitoring 🚧 PLANNED
1. 🚧 Build A/B testing framework
2. 🚧 Implement metrics collection dashboard
3. 🚧 Add bias monitoring
4. 🚧 Create performance dashboards

#### Phase 5: Production ML Models 🚧 FUTURE
1. 🚧 Train dual-tower model with real data
2. 🚧 Build feature engineering pipeline
3. 🚧 Implement online learning
4. 🚧 Deploy model serving infrastructure

### Quick Start Example

```python
import asyncio
from Recommendation.core.recommendation_engine import RecommendationEngine
from Recommendation.config.rec_config import RecommendationConfig

async def main():
    # Initialize engine with default config
    engine = RecommendationEngine()
    
    # Or with custom config
    config = RecommendationConfig(
        exploration_strategy="ucb",
        safety_threshold=0.8,
        cache_ttl=600  # 10 minutes
    )
    engine = RecommendationEngine(config)
    
    # Get recommendations for user
    response = await engine.recommend(
        user_id="agent_001",
        num_results=100,
        context={"device": "mobile", "time": "evening"}
    )
    
    print(f"Generated {len(response.recommendations)} recommendations")
    print(f"Latency: {response.latency * 1000:.2f}ms")
    print(f"Cached: {response.metadata.get('cached', False)}")
    print(f"Candidates: {response.metadata.get('candidate_count', 0)}")
    
    # Access recommendations
    for i, rec in enumerate(response.recommendations[:5]):
        print(f"{i+1}. {rec.get('id')} - Score: {rec.get('utility', 0):.3f}")
    
    # Record user interaction
    await engine.record_interaction(
        user_id="agent_001",
        content_id="feed_12345",
        interaction_type="like",
        dwell_time=30.5
    )
    
    # Get engine statistics
    stats = engine.get_statistics()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Avg latency: {stats['average_latency_ms']:.2f}ms")
    print(f"Cache size: {stats['cache_size']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**See also**: `examples/recommendation_example.py` for complete working example

---

## 📝 Trace Logging

**CRITICAL**: Use file-based trace logging. **NO console logs**.

**Location**: `utils/logger.py`

### Logger Usage

```python
from Recommendation.utils.logger import get_logger

# Get logger for component (creates trace/recommendation/{component_name}.log)
logger = get_logger("heavy_ranker", component="recommendation")

# Log recommendation request
logger.info("Generating recommendations", extra={
    "user_id": user_id,
    "candidate_count": len(candidates),
    "request_id": request_id
})

# Log ranking latency
logger.debug("Ranking completed", extra={
    "user_id": user_id,
    "latency_ms": latency * 1000,
    "candidates_ranked": len(ranked)
})

# Log errors
logger.error("Ranking failed", extra={
    "user_id": user_id,
    "error": str(e)
})
```

### Performance Decorators

**Location**: `utils/decorators.py`

```python
from Recommendation.utils.decorators import log_performance, log_errors, trace_execution

# Log performance metrics automatically
@log_performance(log_args=True, log_result=False)
async def rank_candidates(candidates, user_id):
    # Function timing and args logged automatically
    return ranked_candidates

# Log errors with stack traces
@log_errors(reraise=True)
async def critical_operation():
    # Errors logged automatically with full context
    pass

# Complete tracing (performance + errors + entry/exit)
@trace_execution(component="candidate")
async def generate_candidates(user_id: str):
    # Fully traced execution
    pass
```

### Request Tracing

**Location**: `utils/trace_request.py`

```python
from Recommendation.utils.trace_request import RequestTracer

# Initialize tracer
tracer = RequestTracer(trace_dir="trace")

# Trace a specific request through the pipeline
trace = tracer.trace_recommendation_flow("req_12345")

# Print human-readable trace
tracer.print_recommendation_flow("req_12345")

# Compare two requests
comparison = tracer.compare_requests("req_12345", "req_12346")
```

### Log Files

All logs stored in `trace/recommendation/`:
- `recommendation_engine.log` - Main engine logs
- `candidate_sourcing.log` - Candidate generation
- `in_network_source.log` - In-network sourcing
- `out_network_source.log` - Out-of-network sourcing
- `social_proof_source.log` - Social proof sourcing
- `light_ranker.log` - Light ranking
- `heavy_ranker.log` - Heavy ranking
- `exploration_engine.log` - Exploration strategies
- `diversity_injector.log` - Diversity injection
- `safety_filter.log` - Safety filtering

**See also**: `LOGGING_SYSTEM.md` for complete logging documentation

---

## 📚 API Reference

### RecommendationEngine API

**Implemented Methods:**

```python
# Core recommendation (Step 7: Serving)
async def recommend(
    user_id: str, 
    num_results: int = 100, 
    context: Optional[Dict[str, Any]] = None
) -> RecommendationResponse
"""
Generate personalized recommendations for user.

Args:
    user_id: User/Agent ID
    num_results: Number of recommendations to return (default: 100)
    context: Additional context (device, time, location, etc.)

Returns:
    RecommendationResponse with:
    - recommendations: List of recommended content
    - latency: Request latency in seconds
    - metadata: Pipeline statistics (cached, candidate_count, filtered_count)
"""

# Feedback collection
async def record_interaction(
    user_id: str, 
    content_id: str, 
    interaction_type: str, 
    **kwargs
) -> None
"""
Record user interaction with content for future model updates.

Args:
    user_id: User ID
    content_id: Content ID that was interacted with
    interaction_type: Type of interaction (like, share, view, etc.)
    **kwargs: Additional interaction data (dwell_time, etc.)
"""

# Statistics
def get_statistics() -> Dict[str, Any]
"""
Get recommendation engine statistics.

Returns:
    Dictionary with:
    - total_requests: Total number of recommendation requests
    - average_latency_ms: Average latency per request
    - cache_size: Number of cached recommendation sets
"""
```

### RecommendationResponse

```python
class RecommendationResponse:
    """Recommendation response object"""
    
    recommendations: List[Any]  # List of recommended content
    latency: float              # Request latency in seconds
    metadata: Dict[str, Any]    # Additional metadata
    # metadata includes:
    # - cached: bool - Whether result was from cache
    # - pipeline_steps: int - Number of pipeline steps (7)
    # - candidate_count: int - Initial candidate pool size
    # - filtered_count: int - Number of items filtered out
```

### ExplorationEngine API

```python
async def apply_exploration(
    ranked: List[Dict[str, Any]], 
    user_id: str
) -> List[Dict[str, Any]]
"""Apply exploration strategy (ε-greedy, UCB, or Thompson Sampling)"""

def record_impression(
    content_id: str, 
    engagement: bool, 
    reward: float = 0.0
) -> None
"""Record content impression for exploration learning"""
```

### RequestTracer API (Debugging & Monitoring)

```python
def trace_recommendation_flow(request_id: str) -> Dict[str, Any]
"""Trace a recommendation request through the pipeline"""

def print_recommendation_flow(request_id: str)
"""Print recommendation flow in readable format"""

def compare_requests(request_id1: str, request_id2: str) -> Dict[str, Any]
"""Compare two requests to identify differences"""
```

### 🚧 Future APIs (Planned)

```python
# Model training (not yet implemented)
async def train_models(training_data: TrainingData) -> TrainingMetrics

# A/B testing (not yet implemented)
async def create_experiment(config: ExperimentConfig) -> Experiment
async def get_experiment_results(experiment_id: str) -> ExperimentResults
```

---

## 🤝 Contributing

When contributing to Recommendation module:

1. **Follow Pipeline Structure** - Maintain 7-step architecture
2. **Performance First** - Optimize for < 100ms latency
3. **Use Trace Logging** - Never use console logs
4. **Test Ranking Quality** - Verify recommendation relevance
5. **Monitor Bias** - Track and mitigate algorithmic bias

---

## 📖 Related Documentation

- [Arena Module](../Arena/README.md)
- [Agent Module](../Agent/README.md)
- [Feed Module](../Feed/README.md)
- [Twitter Algorithm Reference](https://github.com/twitter/the-algorithm)

---

**Recommendation - The Intelligence Layer of Social-Arena** 🎯🧠

*Personalized content delivery at scale with exploration and diversity*
