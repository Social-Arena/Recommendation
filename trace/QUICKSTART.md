# Trace Logging System - Quick Start Guide

## Overview

The trace logging system provides comprehensive debugging capabilities for the Twitter Recommendation Engine. All runtime logs are stored in structured JSON format for easy analysis.

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
└── archived/         # Archived logs (auto-rotated)
```

## Quick Start

### 1. Basic Logging in Your Code

```python
from utils.logger import get_logger

# Create a logger for your component
logger = get_logger(__name__, component="candidate", level="INFO")

# Log messages with context
logger.info("Processing started", extra={
    "user_id": user_id,
    "count": 100,
    "operation": "candidate_generation"
})

# Log errors with stack traces
try:
    result = process_data()
except Exception as e:
    logger.error("Processing failed", exc_info=True, extra={
        "user_id": user_id,
        "error_type": type(e).__name__
    })
```

### 2. Using Decorators for Automatic Logging

```python
from utils.decorators import log_performance, log_errors, trace_execution

# Track performance automatically
@log_performance(log_args=True)
async def generate_candidates(user_id: str) -> List[str]:
    # Function execution time is logged automatically
    pass

# Log errors automatically
@log_errors(reraise=True)
def process_item(item_id: str):
    # Errors are logged with full stack traces
    pass

# Full tracing (entry/exit/performance/errors)
@trace_execution(component="serving")
async def serve_recommendations(user_id: str):
    # Everything is logged automatically
    pass
```

### 3. Request Context for Tracing

```python
from utils.logger import LogContext

# Set context for the entire request
with LogContext(request_id=request_id, user_id=user_id):
    # All logs within this block will include request_id and user_id
    logger.info("Processing request")
    result = await process_request()
```

### 4. Run the Example

```bash
# Run the logging example to see it in action
cd /home/user/Recommendation
python examples/logging_example.py
```

This will generate sample logs in the `trace/logs/` directory.

## Analyzing Logs

### 1. Trace a Specific Request

```bash
# View all logs for a specific request
python utils/trace_request.py <request_id>

# Export trace to JSON
python utils/trace_request.py <request_id> --export trace.json
```

### 2. Find Errors

```bash
# Find all errors in the last hour
python utils/log_analyzer.py errors --since "2025-11-16T10:00:00"

# Find errors for a specific component
python utils/log_analyzer.py errors --component candidate

# Find specific error types
python utils/log_analyzer.py errors --type ValueError
```

### 3. Analyze Performance

```bash
# Analyze performance for a component
python utils/log_analyzer.py performance candidate

# Find slow operations (> 1000ms)
python utils/log_analyzer.py slow candidate --threshold 1000
```

### 4. Programmatic Analysis

```python
from utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()

# Find errors
errors = analyzer.find_errors(component="candidate", since=datetime.now() - timedelta(hours=1))

# Trace a request
request_logs = analyzer.trace_request("request-id-here")

# Analyze performance
perf_stats = analyzer.analyze_performance("candidate")
print(f"Mean duration: {perf_stats['duration_ms']['mean']} ms")
print(f"P95: {perf_stats['duration_ms']['p95']} ms")
```

## Debugging Workflow

When you encounter an issue:

1. **Get the Request ID**: From error messages or user reports

2. **Trace the Request**:
   ```bash
   python utils/trace_request.py <request_id>
   ```

3. **Identify the Stage**: Look at which pipeline stage failed
   - Candidate Generation
   - Light Ranking
   - Heavy Ranking
   - Exploration
   - Diversity Injection
   - Safety Filter
   - Serving

4. **Check Component Logs**: Dive into specific component logs
   ```bash
   python utils/log_analyzer.py errors --component <component_name>
   ```

5. **Analyze Performance**: Check if it's a performance issue
   ```bash
   python utils/log_analyzer.py slow <component_name>
   ```

6. **Review Stack Traces**: Check error logs for detailed stack traces
   - Located in `trace/logs/errors/`
   - Contains full exception information

## Log Levels

Use appropriate log levels:

- **TRACE**: Very detailed, step-by-step execution (use sparingly)
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about system operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures
- **CRITICAL**: Critical errors that may cause system failure

## Best Practices

### 1. Always Include Context

```python
# Good
logger.info("Candidates generated", extra={
    "user_id": user_id,
    "candidate_count": len(candidates),
    "sources": ["in_network", "out_network"]
})

# Bad
logger.info("Candidates generated")
```

### 2. Use Decorators for Functions

```python
# Good - automatic performance tracking
@log_performance()
async def expensive_operation():
    pass

# Tedious - manual tracking
async def expensive_operation():
    start = time.time()
    try:
        result = await do_work()
        logger.info("Operation completed", extra={"duration": time.time() - start})
        return result
    except Exception as e:
        logger.error("Failed", exc_info=True)
        raise
```

### 3. Set Request Context Early

```python
# Good - context for entire request
with LogContext(request_id=request_id, user_id=user_id):
    await process_request()

# Bad - manually passing context everywhere
await process_request(request_id, user_id)
```

### 4. Log Structured Data

```python
# Good - structured, parseable
logger.info("Ranking completed", extra={
    "candidates_in": 1500,
    "candidates_out": 100,
    "duration_ms": 45.2
})

# Bad - unstructured string
logger.info(f"Ranked {1500} candidates down to {100} in 45.2ms")
```

### 5. Don't Log Sensitive Data

```python
# Good - redacted
logger.info("User logged in", extra={
    "user_id": user_id,
    "password": "***REDACTED***"
})

# Bad - exposes secrets
logger.info("User logged in", extra={
    "user_id": user_id,
    "password": actual_password
})
```

## Common Issues

### Issue: Logs not appearing

**Solution**: Check that:
1. Logger is created with correct component name
2. Log level is appropriate (DEBUG/INFO/etc)
3. `trace/logs/` directory exists
4. No permission issues on directory

### Issue: Can't find request logs

**Solution**:
1. Verify request_id is being set:
   ```python
   with LogContext(request_id=request_id):
       # your code
   ```
2. Check if logs exist:
   ```bash
   grep -r "request_id" trace/logs/
   ```

### Issue: Log files too large

**Solution**: Logs are auto-rotated:
- Main logs: Rotate at 100MB
- Daily logs: Rotate daily
- Archives kept for 30 days

Manual cleanup:
```bash
# Remove old archives
rm -rf trace/archived/*

# Clear all logs (development only)
find trace/logs -name "*.log" -delete
```

## Tips for Effective Debugging

1. **Use Request IDs**: Always set request context for traceability
2. **Log at Decision Points**: Log when making important decisions
3. **Include Metrics**: Log counts, durations, scores for analysis
4. **Log Errors with Context**: Include what you were trying to do when error occurred
5. **Use Performance Logs**: Track slow operations proactively
6. **Review Logs Regularly**: Don't wait for issues to check logs

## Integration with Development Workflow

### During Development

```python
# Use DEBUG level for detailed logging
logger = get_logger(__name__, component="candidate", level="DEBUG")

# Use TRACE for very detailed debugging
logger.trace("Entering loop iteration", extra={"iteration": i})
```

### During Testing

```python
# Check logs after tests
from utils.log_analyzer import LogAnalyzer

def test_recommendation_flow():
    analyzer = LogAnalyzer()

    # Run test
    result = generate_recommendations(user_id, request_id)

    # Verify no errors occurred
    errors = analyzer.trace_request(request_id)
    assert not any(log['level'] == 'ERROR' for log in errors)
```

### In Production

```python
# Use INFO level in production
logger = get_logger(__name__, component="serving", level="INFO")

# Log important events only
logger.info("Recommendation request served", extra={
    "user_id": user_id,
    "num_recommendations": len(results),
    "duration_ms": duration
})
```

## Support

For issues with the logging system:
1. Check this guide
2. Review `trace/README.md` for detailed documentation
3. Run example: `python examples/logging_example.py`
4. Check generated logs in `trace/logs/`
