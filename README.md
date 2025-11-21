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

### Key Features

- **7-Step Recommendation Pipeline**: Complete flow from candidate sourcing to serving
- **Dual-Tower Model**: User tower + Content tower for efficient embedding
- **Multi-Task Learning**: Predict likes, retweets, replies, dwell time, negative feedback
- **Exploration Engine**: ε-greedy, UCB, Thompson Sampling strategies
- **Diversity Injection**: Topic, author, and content type diversity
- **Safety Filtering**: Toxicity, misinformation, harmful content detection
- **A/B Testing**: Hot-swappable recommendation strategies
- **Real-time Serving**: < 100ms latency for recommendations

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
recommendation/
│
├── models/                        # ML models
│   ├── __init__.py
│   ├── two_tower_model.py        # Dual-tower recommendation model
│   ├── candidate_generation.py   # Candidate generation models
│   ├── heavy_ranker.py           # Heavy ranking model
│   └── light_ranker.py           # Light ranking model
│
├── sourcing/                      # Candidate sources
│   ├── __init__.py
│   ├── in_network_source.py      # In-network content source
│   ├── out_network_source.py     # Out-of-network content source
│   ├── social_proof_source.py    # Social proof source
│   └── trending_source.py        # Trending content source
│
├── ranking/                       # Ranking systems
│   ├── __init__.py
│   ├── utility_scorer.py         # Utility scoring
│   ├── multi_task_model.py       # Multi-task prediction model
│   ├── exploration_engine.py     # Exploration strategies
│   └── diversity_injector.py     # Diversity injection
│
├── filters/                       # Filtering systems
│   ├── __init__.py
│   ├── safety_filter.py          # Safety filtering
│   ├── quality_filter.py         # Quality filtering
│   ├── dedup_filter.py           # Deduplication filter
│   └── personalization_filter.py # Personalization filter
│
├── serving/                       # Serving infrastructure
│   ├── __init__.py
│   ├── feed_mixer.py             # Feed mixing
│   ├── real_time_ranker.py       # Real-time ranking
│   ├── ab_test_framework.py      # A/B testing
│   └── recommendation_api.py     # Recommendation API
│
├── monitoring/                    # Monitoring
│   ├── __init__.py
│   ├── rec_metrics.py            # Recommendation metrics
│   ├── bias_monitor.py           # Bias monitoring
│   └── feedback_collector.py     # Feedback collection
│
├── tests/                         # Test suite
│   ├── test_sourcing.py
│   ├── test_ranking.py
│   ├── test_serving.py
│   └── test_ab_testing.py
│
└── README.md                      # This file
```

---

## 🔄 7-Step Pipeline

### Step 1: Candidate Sourcing

**Goal**: Generate a candidate pool of ~1500 content items per user

```python
class CandidateSourcing:
    """Generate candidate pool from multiple sources"""
    
    async def generate_candidates(self, user_id: str) -> List[CandidateContent]:
        # In-Network: Content from followed authors
        in_network = await self.in_network_source.generate_candidates(user_id)
        
        # Out-of-Network: Interest-based, trending, friend interactions
        out_network = await self.out_network_source.generate_candidates(user_id)
        
        # Social Proof: Content friends engaged with
        social_proof = await self.social_proof_source.generate_candidates(user_id)
        
        # Merge and deduplicate
        candidates = self._merge_candidates([in_network, out_network, social_proof])
        candidates = self._deduplicate(candidates)
        
        return candidates[:1500]
```

**Key Sources**:
- **In-Network** (40%): Authors the user follows
- **Out-of-Network** (50%): Interest clusters, trending, similar users
- **Social Proof** (10%): Friend interactions, network signals

---

### Step 2: Light Ranking

**Goal**: Fast initial ranking to reduce candidate pool

```python
class LightRanker:
    """Fast ranking with lightweight features"""
    
    async def rank(self, candidates: List[CandidateContent], user: User) -> List[ScoredContent]:
        ranked = []
        
        for candidate in candidates:
            # Extract lightweight features
            features = self._extract_light_features(candidate, user)
            
            # Compute light score
            score = self._compute_light_score(features)
            
            ranked.append(ScoredContent(content=candidate, light_score=score))
        
        # Return top candidates for heavy ranking
        return sorted(ranked, key=lambda x: x.light_score, reverse=True)[:500]
```

**Light Features**:
- Content age
- Engagement velocity (likes/hour)
- Author follower count
- User-author interaction history
- Topic match score

---

### Step 3: Heavy Ranking (Multi-Task)

**Goal**: Precise ranking with multi-task predictions

```python
class HeavyRanker:
    """Heavy ranking with multi-task model"""
    
    def __init__(self):
        self.multi_task_model = MultiTaskModel()
        self.utility_scorer = UtilityScorer()
    
    async def rank(self, candidates: List[ScoredContent], user: User) -> List[RankedContent]:
        ranked = []
        
        for candidate in candidates:
            # Extract deep features
            features = self._extract_deep_features(candidate, user)
            
            # Multi-task predictions
            predictions = self.multi_task_model.predict(features)
            # - P(like), P(retweet), P(reply), P(click)
            # - Expected dwell time
            # - P(negative feedback)
            
            # Compute utility score
            utility = self.utility_scorer.score(predictions, user.preferences)
            
            ranked.append(RankedContent(content=candidate, utility=utility, predictions=predictions))
        
        return sorted(ranked, key=lambda x: x.utility, reverse=True)
```

**Multi-Task Predictions**:
- **Positive Actions**: Like, Retweet, Reply, Click, Dwell Time
- **Negative Actions**: Report, Block, Mute, Hide

**Utility Function**:
```
utility = w_like * P(like) + w_rt * P(retweet) + w_reply * P(reply) 
        + w_dwell * E(dwell_time) - w_neg * P(negative)
```

---

### Step 4: Exploration Engine

**Goal**: Balance exploitation and exploration

```python
class ExplorationEngine:
    """Exploration strategies for discovery"""
    
    def __init__(self, strategy: str = "epsilon_greedy"):
        self.strategy = strategy
        self.epsilon = 0.1  # Exploration rate
    
    async def apply_exploration(self, ranked: List[RankedContent], user: User) -> List[RankedContent]:
        if self.strategy == "epsilon_greedy":
            return self._epsilon_greedy(ranked, user)
        elif self.strategy == "ucb":
            return self._ucb(ranked, user)
        elif self.strategy == "thompson_sampling":
            return self._thompson_sampling(ranked, user)
    
    def _epsilon_greedy(self, ranked: List[RankedContent], user: User) -> List[RankedContent]:
        """Randomly promote some content with probability ε"""
        explored = ranked.copy()
        
        for i in range(len(explored)):
            if random.random() < self.epsilon:
                # Randomly boost this item
                explored[i].utility += random.uniform(0, 0.5)
        
        return sorted(explored, key=lambda x: x.utility, reverse=True)
    
    def _ucb(self, ranked: List[RankedContent], user: User) -> List[RankedContent]:
        """Upper Confidence Bound exploration"""
        explored = []
        
        for content in ranked:
            # Get historical stats
            stats = self._get_content_stats(content.content.id)
            
            # UCB bonus
            ucb_bonus = self._calculate_ucb_bonus(stats)
            
            # Adjusted score
            adjusted_utility = content.utility + ucb_bonus
            
            explored.append(RankedContent(content=content.content, utility=adjusted_utility))
        
        return sorted(explored, key=lambda x: x.utility, reverse=True)
```

**Strategies**:
- **ε-greedy**: Random exploration with probability ε
- **UCB**: Upper Confidence Bound for systematic exploration
- **Thompson Sampling**: Bayesian approach to exploration

---

### Step 5: Diversity Injection

**Goal**: Ensure diverse, non-repetitive feed

```python
class DiversityInjector:
    """Inject diversity constraints"""
    
    async def inject_diversity(self, ranked: List[RankedContent], config: DiversityConfig) -> List[RankedContent]:
        diversified = []
        
        # Track diversity metrics
        topics_seen = set()
        authors_seen = set()
        
        for content in ranked:
            # Check diversity constraints
            if self._meets_diversity_constraints(content, topics_seen, authors_seen, config):
                diversified.append(content)
                
                # Update tracking
                topics_seen.update(content.topics)
                authors_seen.add(content.author_id)
            
            if len(diversified) >= config.target_size:
                break
        
        return diversified
    
    def _meets_diversity_constraints(self, content, topics_seen, authors_seen, config):
        """Check if content meets diversity constraints"""
        # Topic diversity
        topic_overlap = len(set(content.topics) & topics_seen) / max(len(content.topics), 1)
        if topic_overlap > config.max_topic_repetition:
            return False
        
        # Author diversity
        if authors_seen.count(content.author_id) >= config.max_same_author:
            return False
        
        # Content similarity
        if self._is_too_similar_to_recent(content, diversified):
            return False
        
        return True
```

**Diversity Dimensions**:
- **Topic Diversity**: Limit same topics
- **Author Diversity**: Limit same authors
- **Content Type**: Mix text, images, videos
- **Sentiment**: Balance positive/negative
- **Freshness**: Mix new and proven content

---

### Step 6: Safety Filtering

**Goal**: Remove unsafe, low-quality content

```python
class SafetyFilter:
    """Filter unsafe and low-quality content"""
    
    async def filter(self, candidates: List[RankedContent]) -> List[RankedContent]:
        filtered = []
        
        for content in candidates:
            # Safety checks
            safety_score = await self._assess_safety(content)
            
            if safety_score >= self.safety_threshold:
                filtered.append(content)
            else:
                # Log filtered content
                self._log_filtered_content(content, safety_score)
        
        return filtered
    
    async def _assess_safety(self, content: RankedContent) -> float:
        """Assess content safety"""
        checks = {
            'toxicity': self.toxicity_detector.score(content.text),
            'misinformation': self.misinfo_detector.score(content),
            'spam': self.spam_detector.score(content),
            'nsfw': self.nsfw_detector.score(content)
        }
        
        # Weighted safety score
        safety = 1.0
        for check_type, score in checks.items():
            if score > self.thresholds[check_type]:
                safety *= (1 - score)
        
        return safety
```

**Safety Checks**:
- Toxicity detection
- Misinformation detection
- Spam detection
- NSFW content detection
- Brand safety

---

### Step 7: Real-time Serving

**Goal**: Serve recommendations with < 100ms latency

```python
class RecommendationAPI:
    """Real-time recommendation serving"""
    
    async def get_recommendations(self, user_id: str, context: RequestContext) -> RecommendationResponse:
        # Check cache
        cached = await self.cache.get(user_id)
        if cached and not cached.is_stale():
            return cached
        
        # Generate fresh recommendations
        start_time = time.time()
        
        # Run full pipeline
        candidates = await self.sourcing.generate_candidates(user_id)
        light_ranked = await self.light_ranker.rank(candidates, user_id)
        heavy_ranked = await self.heavy_ranker.rank(light_ranked, user_id)
        explored = await self.exploration_engine.apply(heavy_ranked, user_id)
        diversified = await self.diversity_injector.inject(explored)
        filtered = await self.safety_filter.filter(diversified)
        
        # Mix with real-time signals
        final = await self.feed_mixer.mix(filtered, context)
        
        latency = time.time() - start_time
        
        # Cache results
        await self.cache.set(user_id, final, ttl=300)
        
        # Log metrics
        self._log_serving_metrics(user_id, latency, len(final))
        
        return RecommendationResponse(recommendations=final, latency=latency)
```

---

## 🏛️ Dual-Tower Model

### Architecture

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

### Implementation

```python
class TwoTowerModel(nn.Module):
    """Dual-tower recommendation model"""
    
    def __init__(self, config: ModelConfig):
        super().__init__()
        
        # User tower
        self.user_tower = nn.Sequential(
            nn.Embedding(config.num_users, 256),
            nn.Linear(256 + config.user_feature_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )
        
        # Content tower
        self.content_tower = nn.Sequential(
            nn.Embedding(config.num_contents, 256),
            nn.Linear(256 + config.content_feature_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128)
        )
    
    def forward(self, user_features, content_features):
        # Get embeddings
        user_embedding = self.user_tower(user_features)
        content_embedding = self.content_tower(content_features)
        
        # Compute similarity
        similarity = torch.sum(user_embedding * content_embedding, dim=-1)
        
        return similarity
```

**Benefits**:
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

```python
from recommendation.config import RecommendationConfig

config = RecommendationConfig(
    # Candidate sourcing
    candidate_pool_size=1500,
    in_network_ratio=0.4,
    out_network_ratio=0.5,
    social_proof_ratio=0.1,
    
    # Ranking
    light_ranking_top_k=500,
    heavy_ranking_top_k=100,
    
    # Exploration
    exploration_strategy="epsilon_greedy",
    epsilon=0.1,
    
    # Diversity
    max_same_author=2,
    max_topic_repetition=0.3,
    
    # Safety
    safety_threshold=0.7,
    enable_toxicity_filter=True,
    
    # Serving
    cache_ttl=300,  # seconds
    target_latency=100,  # ms
    
    # A/B testing
    enable_ab_testing=True,
    default_experiment_duration=7  # days
)
```

---

## 🛠️ Development Guide

### Development Priority

#### Phase 1: Candidate Sourcing 🚧
1. Implement In-Network source
2. Implement Out-of-Network source
3. Implement Social Proof source
4. Build candidate deduplication

#### Phase 2: Ranking Systems
1. Implement Light Ranker
2. Implement Heavy Ranker with multi-task model
3. Build Utility Scorer
4. Train dual-tower model

#### Phase 3: Exploration & Diversity
1. Implement exploration strategies
2. Build diversity injector
3. Add safety filters
4. Optimize serving latency

#### Phase 4: A/B Testing & Monitoring
1. Build A/B testing framework
2. Implement metrics collection
3. Add bias monitoring
4. Create dashboards

### Quick Start Example

```python
from recommendation import RecommendationEngine

# Initialize engine
engine = RecommendationEngine(config)

# Get recommendations for user
recommendations = await engine.recommend(
    user_id="agent_001",
    num_results=100,
    context={"device": "mobile", "time": "evening"}
)

# Process feedback
await engine.record_interaction(
    user_id="agent_001",
    content_id="feed_12345",
    interaction_type="like",
    dwell_time=30.5
)
```

---

## 📝 Trace Logging

**CRITICAL**: Use file-based trace logging. **NO console logs**.

```python
from recommendation.utils.logger import get_logger

logger = get_logger(__name__, component="heavy_ranker")

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
```

---

## 📚 API Reference

### RecommendationEngine API

```python
# Core recommendation
async def recommend(user_id: str, num_results: int, context: dict) -> RecommendationResponse

# Feedback collection
async def record_interaction(user_id: str, content_id: str, interaction_type: str, **kwargs) -> None

# Model training
async def train_models(training_data: TrainingData) -> TrainingMetrics

# A/B testing
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
