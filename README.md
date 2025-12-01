# Social Arena - Recommendation Engine 🎯

A comprehensive Twitter-style recommendation system implementing advanced algorithms for social media viral propagation simulation. Built with dual-tower architecture, exploration-exploitation balance, and comprehensive A/B testing framework.

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/Social-Arena/Recommendation.git
cd Recommendation

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Initialize submodules (Agent and Feed libraries)
git submodule update --init --recursive

# Install the package and all dependencies
pip install -e .
pip install -e external/Feed
pip install -e external/Agent
```

### Basic Usage

```python
from recommendation import CentralizedRecommendationSystem, BalancedStrategy
import feed
from agent import Agent

# Initialize recommendation system
rec_system = CentralizedRecommendationSystem(
    strategy=BalancedStrategy(explore_ratio=0.2)
)

# Create agents
agent = Agent(agent_id="001", username="alice", bio="Tech enthusiast")
rec_system.add_agent("001", {"interests": ["tech", "AI"]})

# Create and ingest content
new_feed = feed.Feed(
    id=feed.generate_feed_id(),
    text="Hello Social Arena! #AI #Python",
    author_id="001",
    feed_type="post"
)
rec_system.ingest_feed(new_feed)

# Get personalized recommendations
recommendations = rec_system.fetch("001", {"max_feeds": 10})
print(f"Showing {len(recommendations['feeds'])} personalized feeds")
```

## 📊 Core Features

### 🐦 Twitter Algorithm Implementation
- **7-Stage Pipeline**: Complete replication of Twitter's recommendation system
  - Candidate Generation (In-Network + Out-of-Network)  
  - Light Ranking (Fast scoring of candidates)
  - Heavy Ranking (Multi-task deep learning model)
  - Exploration Engine (ε-greedy, UCB, Thompson Sampling)
  - Diversity Injection (Content and author diversity)
  - Safety Filtering (Content moderation)
  - Real-time Serving (Low-latency delivery)

### 🏗️ Advanced Architecture
- **Dual-Tower Model**: Separate user and content embedding towers
- **Multi-Task Learning**: Simultaneous optimization for engagement, satisfaction, and safety
- **Real-Time Inference**: Sub-100ms response times
- **Scalable Design**: Handles millions of candidates efficiently

### 🧪 Experimentation Framework
- **A/B Testing**: Hot-swappable recommendation strategies
- **Multi-Armed Bandits**: Dynamic strategy selection
- **Performance Monitoring**: Real-time metrics and alerts
- **Strategy Comparison**: Side-by-side algorithm evaluation

## 🛠️ System Components

### Core Modules

```
Recommendation/
├── recommendation/             # Core recommendation package
│   ├── __init__.py            # Package exports
│   ├── base.py                # Base classes and protocols
│   ├── system.py              # Main recommendation system
│   ├── strategies.py          # Ranking strategies
│   └── example.py             # Usage example
├── external/                  # External dependencies
│   ├── Agent/                 # AI agent framework
│   └── Feed/                  # Twitter data structures
├── utils/                     # Logging and utilities
│   ├── logger.py              # Centralized logging
│   ├── decorators.py          # Performance tracking
│   ├── log_analyzer.py        # Log analysis tools
│   └── trace_request.py       # Request tracing
└── trace/                     # Runtime logs
    └── logs/                  # Component-specific logs
```

### Recommendation Pipeline

```python
# 1. Candidate Generation
candidates = candidate_generator.generate(
    user_id="user_123",
    in_network_size=1000,
    out_network_size=500
)

# 2. Light Ranking
light_scores = light_ranker.score(candidates, user_features)

# 3. Heavy Ranking  
heavy_scores = heavy_ranker.score(
    top_candidates=light_scores[:100],
    user_embedding=user_tower(user_features),
    content_embeddings=content_tower(candidate_features)
)

# 4. Exploration
explored_scores = exploration_engine.apply(
    scores=heavy_scores,
    strategy="epsilon_greedy",
    epsilon=0.1
)

# 5. Diversity Injection
diverse_results = diversity_injector.inject(
    scored_candidates=explored_scores,
    diversity_weight=0.3
)

# 6. Safety Filtering
safe_results = safety_filter.filter(diverse_results)

# 7. Serving
recommendations = serving_engine.format_response(safe_results)
```

## 🔍 Trace Logging System

**CRITICAL**: All debugging uses file-based logging - **NO console output**.

### Log Structure
```
trace/logs/
├── candidate/          # Candidate generation logs
├── ranking/           # Ranking system logs  
├── exploration/       # Exploration engine logs
├── diversity/         # Diversity injection logs
├── serving/          # Real-time serving logs
├── ab_test/          # A/B testing logs
├── feedback/         # User feedback logs
├── errors/           # All error logs
└── performance/      # Performance metrics
```

### Debugging Workflow
```bash
# Test logging system
python test_logging.py

# Trace specific request
python utils/trace_request.py req_12345

# Analyze errors
python utils/log_analyzer.py errors --component ranking

# Performance analysis
python utils/log_analyzer.py performance --timeframe 1h
```

### Usage Example
```python
from utils import get_logger, log_performance, LogContext

logger = get_logger("HeavyRanker", component="ranking")

@log_performance()
def rank_candidates(candidates, user_features):
    with LogContext(request_id="req_123"):
        logger.info(f"Ranking {len(candidates)} candidates")
        # Ranking logic here
        logger.debug("Model inference completed")
        return ranked_results
```

## 📈 Performance Metrics

### Key Metrics Tracked
- **Engagement Rate**: Likes, retweets, replies per recommendation
- **Click-Through Rate**: Content consumption metrics
- **Dwell Time**: Time spent viewing recommended content
- **Diversity Score**: Content and author diversity metrics
- **Exploration Rate**: Novel content discovery percentage
- **Safety Score**: Content moderation effectiveness

### A/B Testing Results
```python
# Example A/B test comparison
{
    "epsilon_greedy_0.1": {
        "engagement_rate": 0.045,
        "diversity_score": 0.73,
        "exploration_rate": 0.12
    },
    "thompson_sampling": {
        "engagement_rate": 0.048,
        "diversity_score": 0.71,
        "exploration_rate": 0.15
    }
}
```

## 🧰 Usage Examples

### Basic Recommendation Generation
```python
from recommendation_engine import RecommendationEngine

engine = RecommendationEngine(
    model_path="models/twitter_v2.pkl",
    config_path="config/production.yaml"
)

recommendations = engine.get_recommendations(
    user_id="user_123",
    num_recommendations=20,
    strategy="thompson_sampling"
)
```

### Custom Exploration Strategy
```python
from strategies import CustomExplorationStrategy

class MyStrategy(CustomExplorationStrategy):
    def apply(self, scores, context):
        # Your custom exploration logic
        return modified_scores

engine.register_strategy("my_strategy", MyStrategy())
```

### Real-time Feedback Integration
```python
# Collect user feedback for online learning
engine.record_feedback(
    user_id="user_123",
    content_id="tweet_456",
    action="like",
    timestamp=datetime.now()
)

# Update model with feedback
engine.update_from_feedback(batch_size=1000)
```

## 🔧 Configuration

### Model Configuration
```yaml
# config/production.yaml
model:
  user_tower_dim: 256
  content_tower_dim: 256
  hidden_layers: [512, 256, 128]
  dropout_rate: 0.3

exploration:
  strategy: "thompson_sampling"
  exploration_rate: 0.1
  update_frequency: 3600

diversity:
  content_diversity_weight: 0.3
  author_diversity_weight: 0.2
  temporal_diversity_weight: 0.1

safety:
  toxicity_threshold: 0.8
  misinformation_threshold: 0.7
  spam_threshold: 0.9
```

### Deployment Configuration
```python
# Production serving configuration
SERVING_CONFIG = {
    "batch_size": 32,
    "max_latency_ms": 100,
    "cache_ttl_seconds": 300,
    "fallback_strategy": "popular_content",
    "monitoring_enabled": True
}
```

## 🧪 Extending the System

### Adding New Ranking Models
```python
from models.base_ranker import BaseRanker

class MyCustomRanker(BaseRanker):
    def score(self, candidates, user_features, context):
        # Your custom scoring logic
        return scores

# Register the new ranker
engine.register_ranker("my_ranker", MyCustomRanker())
```

### Custom Feature Extractors
```python
from features import FeatureExtractor

class MyFeatureExtractor(FeatureExtractor):
    def extract(self, content, user, context):
        # Extract custom features
        return feature_vector

engine.add_feature_extractor(MyFeatureExtractor())
```

## 📋 Development Guidelines

### Code Standards
- **Logging**: Use centralized logging system, no print statements
- **Performance**: Add @log_performance decorators to key functions
- **Testing**: Include unit tests for all new components
- **Documentation**: Document all public APIs

### Adding Components
1. Create component in appropriate directory
2. Add comprehensive logging with component name
3. Include performance monitoring
4. Add unit tests in `tests/`
5. Update configuration files
6. Document in this README

### Debugging Process
1. Check `trace/logs/errors/` for error logs
2. Use `trace_request.py` to follow request flow
3. Analyze performance with `log_analyzer.py`
4. Never debug with console prints - use logs only

## 📚 References

- [Twitter's Recommendation Algorithm](https://github.com/twitter/the-algorithm)
- [Deep Learning for Recommender Systems](https://arxiv.org/abs/1707.07435)
- [Multi-Armed Bandits in Recommendation](https://arxiv.org/abs/1909.03212)
- [Content Diversity in Social Media](https://arxiv.org/abs/2008.11696)

## 🤝 Contributing

1. Follow the logging and performance tracking guidelines
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure all logs are helpful for debugging
5. Test A/B framework with new strategies

## 📄 License

See [LICENSE](LICENSE) file for details.

---

**Part of the Social Arena ecosystem** - Building next-generation social media simulation and recommendation systems.