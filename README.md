# Twitter Recommendation Engine

This is the recommendation system for the social media viral propagation agent simulation. Based on Twitter's recommendation algorithm, it implements a pluggable recommendation layer with dual-tower personalization, diversity control, exploration-exploitation balance, and an A/B testing framework with hot-swappable strategies.

## Reference

Implementation based on: https://github.com/twitter/the-algorithm

## Core Features

- **Twitter Algorithm Replication**: Complete 7-step recommendation pipeline
  - Candidate Generation (In-Network + Out-of-Network)
  - Light Ranking
  - Heavy Ranking (Multi-task Model)
  - Exploration Engine
  - Diversity Injection
  - Safety Filtering
  - Real-time Serving

- **Dual-Tower Model**: User tower and content tower deep learning architecture
- **Exploration-Exploitation**: ε-greedy, UCB, and Thompson Sampling strategies
- **A/B Testing Framework**: Hot-swappable strategy testing

## Trace Logging System

**IMPORTANT**: This system includes a comprehensive trace logging system for debugging. All runtime logs are stored in `trace/logs/` directory - **NO console logging**.

### Quick Start

```bash
# Run logging test
python test_logging.py

# Run full example
python examples/logging_example.py

# Trace a request
python utils/trace_request.py <request_id>

# Find errors
python utils/log_analyzer.py errors --component candidate
```

### Documentation

- **[Logging System Overview](LOGGING_SYSTEM.md)** - Complete system documentation
- **[Quick Start Guide](trace/QUICKSTART.md)** - Get started quickly
- **[Detailed Documentation](trace/README.md)** - In-depth reference

### Log Structure

```
trace/
├── logs/
│   ├── app/          # Application logs
│   ├── candidate/    # Candidate generation
│   ├── ranking/      # Ranking systems
│   ├── exploration/  # Exploration engine
│   ├── diversity/    # Diversity injection
│   ├── serving/      # Real-time serving
│   ├── ab_test/      # A/B testing
│   ├── feedback/     # Feedback collection
│   ├── errors/       # All errors
│   └── performance/  # Performance metrics
├── analysis/         # Analysis results
└── archived/         # Rotated logs
```

### Debugging Workflow

When you report an issue:

1. **Provide the request_id** from the error
2. I will trace the request: `python utils/trace_request.py <request_id>`
3. Identify root cause from logs
4. Fix the issue thoroughly

## Development Status

This is a comprehensive implementation plan. See [development guide](LOGGING_SYSTEM.md) for integration instructions.

## Project Structure

```
Recommendation/
├── utils/                  # Utility modules
│   ├── logger.py          # Logging system
│   ├── decorators.py      # Performance & error decorators
│   ├── log_analyzer.py    # Log analysis tools
│   └── trace_request.py   # Request tracing
├── trace/                 # Runtime logs
│   └── logs/             # Component logs
├── examples/              # Usage examples
│   └── logging_example.py
└── test_logging.py        # Logging system test
```

## Contributing

When adding new components:

1. Use the logging system: `from utils import get_logger, log_performance`
2. Create component logger: `logger = get_logger(__name__, component="your_component")`
3. Add performance decorators: `@log_performance()`
4. Set request context: `with LogContext(request_id=...)`
5. Never use print() - always use logger

See [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) for complete integration guide.
