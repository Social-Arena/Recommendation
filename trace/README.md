# Trace Logging System

## Overview
This directory contains all runtime logs for the Twitter Recommendation Engine. All system components log to structured files here for debugging and analysis.

## Directory Structure

```
trace/
├── logs/              # Active log files
│   ├── app/          # Application-level logs
│   ├── candidate/    # Candidate generation logs
│   ├── ranking/      # Ranking system logs
│   ├── exploration/  # Exploration engine logs
│   ├── diversity/    # Diversity injection logs
│   ├── serving/      # Real-time serving logs
│   ├── ab_test/      # A/B test framework logs
│   ├── feedback/     # Feedback collection logs
│   ├── errors/       # Error logs
│   └── performance/  # Performance metrics logs
├── analysis/         # Log analysis results
└── archived/         # Archived logs (rotated daily/weekly)
```

## Log Levels

- **TRACE**: Most detailed, step-by-step execution
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about system operation
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause system failure

## Log Format

All logs use JSON format for easy parsing:

```json
{
  "timestamp": "2025-11-16T12:34:56.789Z",
  "level": "INFO",
  "component": "CandidateGenerator",
  "session_id": "abc-123-def",
  "user_id": "user_12345",
  "request_id": "req_67890",
  "message": "Generated 1500 candidates",
  "data": {
    "in_network_count": 750,
    "out_network_count": 750,
    "duration_ms": 45
  },
  "context": {
    "function": "generate_candidate_pool",
    "file": "candidate_generation.py",
    "line": 123
  }
}
```

## Usage

### In Python Code

```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Log with context
logger.info("Processing user request", extra={
    "user_id": user_id,
    "request_type": "recommendation",
    "num_items": 10
})

# Log errors with stack trace
try:
    result = process_data()
except Exception as e:
    logger.error("Processing failed", exc_info=True, extra={
        "user_id": user_id,
        "error_type": type(e).__name__
    })
```

### Using Decorators

```python
from utils.logger import log_performance, log_errors

@log_performance(logger)
@log_errors(logger)
async def generate_recommendations(user_id: str):
    # Function automatically logs execution time and errors
    pass
```

## Debugging Workflow

1. **Identify the issue**: Note the timestamp, user_id, or request_id
2. **Locate relevant logs**: Use log analysis tools
3. **Trace execution**: Follow the request through components
4. **Find root cause**: Examine error logs and performance metrics
5. **Fix and verify**: Check logs confirm the fix

## Log Analysis Tools

- `utils/log_analyzer.py`: Analyze logs for patterns and errors
- `utils/trace_request.py`: Trace a specific request through the system
- `utils/performance_analyzer.py`: Analyze performance metrics

## Log Rotation

Logs are automatically rotated:
- **Daily rotation**: For high-volume logs (serving, feedback)
- **Weekly rotation**: For medium-volume logs (candidate, ranking)
- **Size-based**: When log files exceed 100MB

Archived logs are compressed and moved to `trace/archived/`.

## Important Notes

- **NO CONSOLE LOGGING**: All logs must go to files for persistence
- **Include Context**: Always log user_id, request_id, session_id
- **Structured Data**: Use JSON format with extra data fields
- **Performance Impact**: Use appropriate log levels in production
- **PII Handling**: Mask sensitive user data in logs
