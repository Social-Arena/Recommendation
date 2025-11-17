# Twitter Recommendation Engine - Trace Logging System

## Overview

A comprehensive trace logging system has been implemented for the Twitter Recommendation Engine to enable thorough debugging and performance analysis. **All logs are written to files only - no console output** - ensuring all runtime information is persisted for later analysis.

## Key Features

### 1. Structured JSON Logging
- All logs use JSON format for easy parsing and analysis
- Every log entry includes:
  - Timestamp (UTC)
  - Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Component name
  - Function/file/line context
  - Request ID, User ID, Session ID (when available)
  - Custom data fields

### 2. Automatic Log Rotation
- Size-based rotation: 100MB for main logs, 50MB for error logs
- Time-based rotation: Daily logs rotated at midnight
- Archives kept for 30 days

### 3. Component-Based Organization
Logs are organized by component:
- `trace/logs/app/` - Application-level logs
- `trace/logs/candidate/` - Candidate generation
- `trace/logs/ranking/` - Ranking systems
- `trace/logs/exploration/` - Exploration engine
- `trace/logs/diversity/` - Diversity injection
- `trace/logs/serving/` - Real-time serving
- `trace/logs/ab_test/` - A/B testing framework
- `trace/logs/feedback/` - Feedback collection
- `trace/logs/errors/` - All error logs
- `trace/logs/performance/` - Performance metrics

### 4. Request Context Tracking
All logs can be tagged with request context:
```python
with LogContext(request_id=request_id, user_id=user_id):
    # All logs in this block include request_id and user_id
    process_request()
```

### 5. Automatic Performance Tracking
Decorators automatically log function performance:
```python
@log_performance(log_args=True, log_result=False)
async def expensive_operation(user_id: str):
    # Execution time is logged automatically
    pass
```

### 6. Automatic Error Logging
Decorators automatically log errors with stack traces:
```python
@log_errors(reraise=True)
def risky_operation():
    # Errors are logged with full stack traces
    pass
```

### 7. Full Execution Tracing
Combine all features:
```python
@trace_execution(component="serving")
async def serve_recommendations(user_id: str):
    # Entry, exit, performance, and errors all logged
    pass
```

## Directory Structure

```
trace/
├── logs/              # Active log files
│   ├── app/          # Application logs
│   │   ├── app.log            # Main log (rotated at 100MB)
│   │   └── app_daily.log      # Daily log (rotated daily)
│   ├── candidate/    # Candidate generation logs
│   ├── ranking/      # Ranking logs
│   ├── errors/       # Error logs from all components
│   └── performance/  # Performance metrics
├── analysis/         # Log analysis results
└── archived/         # Rotated/archived logs
```

## Usage Examples

### Basic Logging

```python
from utils.logger import get_logger

logger = get_logger(__name__, component="candidate", level="INFO")

logger.info("Processing started", extra={
    "user_id": user_id,
    "num_candidates": 1500
})
```

### With Request Context

```python
from utils.logger import LogContext, get_logger

logger = get_logger(__name__, component="serving")

with LogContext(request_id="req-123", user_id="user-456"):
    logger.info("Request received")
    process_request()
    logger.info("Request completed")
```

### Performance Tracking

```python
from utils.decorators import log_performance

@log_performance(log_args=True)
async def generate_candidates(user_id: str, count: int):
    # Function automatically logs:
    # - Start time
    # - Arguments (safely)
    # - Duration
    # - Success/failure status
    candidates = await fetch_candidates(user_id, count)
    return candidates
```

### Error Handling

```python
from utils.decorators import log_errors

@log_errors(reraise=True)
def critical_operation():
    # Errors automatically logged with:
    # - Exception type
    # - Error message
    # - Full stack trace
    # - Function arguments (safely)
    risky_code()
```

### Full Tracing

```python
from utils.decorators import trace_execution
from utils.logger import LogContext

@trace_execution(component="serving")
async def serve_recommendations(user_id: str):
    # Automatically logs:
    # - Function entry
    # - Performance metrics
    # - Errors with stack traces
    # - Function exit
    return recommendations
```

## Log Analysis Tools

### 1. Trace Request Flow

```bash
# View complete request flow
python utils/trace_request.py <request_id>

# Export to file
python utils/trace_request.py <request_id> --export trace.json
```

Output shows:
- Request timeline
- Pipeline stages (candidate → ranking → exploration → diversity → serving)
- Performance metrics per stage
- All errors encountered
- Stage-by-stage data flow

### 2. Find Errors

```bash
# All errors in last hour
python utils/log_analyzer.py errors --since "2025-11-16T10:00:00"

# Errors for specific component
python utils/log_analyzer.py errors --component candidate

# Specific error type
python utils/log_analyzer.py errors --type ValueError
```

### 3. Analyze Performance

```bash
# Performance stats for component
python utils/log_analyzer.py performance candidate

# Find slow operations (>1000ms)
python utils/log_analyzer.py slow candidate --threshold 1000
```

### 4. Programmatic Analysis

```python
from utils.log_analyzer import LogAnalyzer

analyzer = LogAnalyzer()

# Find errors
errors = analyzer.find_errors(
    component="candidate",
    since=datetime.now() - timedelta(hours=1)
)

# Trace request
logs = analyzer.trace_request("request-id-here")

# Performance analysis
stats = analyzer.analyze_performance("ranking")
print(f"P95 latency: {stats['duration_ms']['p95']} ms")
```

## Debugging Workflow

When debugging an issue:

1. **Identify Request ID** from error message or user report

2. **Trace Request Flow**:
   ```bash
   python utils/trace_request.py <request_id>
   ```

3. **Review Output**:
   - Which stage failed?
   - What was the error?
   - Performance bottlenecks?

4. **Deep Dive into Component**:
   ```bash
   python utils/log_analyzer.py errors --component <component_name>
   ```

5. **Check Performance**:
   ```bash
   python utils/log_analyzer.py slow <component_name>
   ```

6. **Review Raw Logs**:
   ```bash
   cat trace/logs/<component>/<component>.log | grep <request_id> | python -m json.tool
   ```

## Log Entry Format

Every log entry follows this structure:

```json
{
  "timestamp": "2025-11-16T12:34:56.789Z",
  "level": "INFO",
  "component": "CandidateGenerator",
  "request_id": "req-abc-123",
  "user_id": "user-456",
  "session_id": "session-789",
  "message": "Generated candidates",
  "data": {
    "num_candidates": 1500,
    "in_network": 750,
    "out_network": 750,
    "duration_ms": 45.2
  },
  "context": {
    "function": "generate_candidate_pool",
    "file": "candidate_generation.py",
    "line": 123,
    "thread": 12345,
    "process": 67890
  }
}
```

For errors, additional fields are included:

```json
{
  "exception": {
    "type": "ValueError",
    "message": "Invalid candidate count",
    "traceback": "Traceback (most recent call last):\n..."
  }
}
```

## Best Practices

### 1. Always Use Request Context

```python
# Good
with LogContext(request_id=request_id, user_id=user_id):
    process_request()

# Bad - harder to trace
process_request()  # No context
```

### 2. Log Structured Data

```python
# Good
logger.info("Candidates generated", extra={
    "count": len(candidates),
    "sources": ["in_network", "out_network"]
})

# Bad - unstructured
logger.info(f"Generated {len(candidates)} candidates")
```

### 3. Use Appropriate Log Levels

- **TRACE**: Very detailed, step-by-step (use sparingly)
- **DEBUG**: Detailed debugging information
- **INFO**: Normal operations
- **WARNING**: Potential issues
- **ERROR**: Errors requiring attention
- **CRITICAL**: System-threatening errors

### 4. Use Decorators for Functions

```python
# Good - automatic tracking
@log_performance()
@log_errors()
async def process_data():
    pass

# Tedious - manual tracking
async def process_data():
    start = time.time()
    try:
        result = await do_work()
        logger.info("Completed", extra={"duration": time.time() - start})
        return result
    except Exception as e:
        logger.error("Failed", exc_info=True)
        raise
```

### 5. Don't Log Sensitive Data

The system automatically redacts common sensitive fields (password, token, secret, api_key), but be cautious with custom data.

## Testing

Run the test suite:

```bash
# Quick test
python test_logging.py

# Full example
python examples/logging_example.py
```

Both scripts verify:
- Logs are written to correct locations
- JSON format is valid
- Decorators work correctly
- Context tracking works
- Error logging captures stack traces

## Integration Checklist

When adding logging to a new component:

- [ ] Import logger: `from utils.logger import get_logger, LogContext`
- [ ] Create logger: `logger = get_logger(__name__, component="your_component")`
- [ ] Add decorators to key functions: `@log_performance()`, `@log_errors()`
- [ ] Use context for requests: `with LogContext(request_id=...)`
- [ ] Log important events with structured data
- [ ] Never use print() or console.log() - use logger instead
- [ ] Test that logs appear in `trace/logs/your_component/`

## Files Created

### Core System
- `utils/logger.py` - Logger factory and context management
- `utils/decorators.py` - Performance and error decorators
- `utils/log_analyzer.py` - Log analysis tools
- `utils/trace_request.py` - Request tracing utility

### Documentation
- `trace/README.md` - Detailed documentation
- `trace/QUICKSTART.md` - Quick start guide
- `LOGGING_SYSTEM.md` - This file

### Examples & Tests
- `examples/logging_example.py` - Complete usage examples
- `test_logging.py` - Quick verification test

### Directory Structure
- `trace/logs/*/` - Component-specific log directories
- `trace/analysis/` - Analysis results
- `trace/archived/` - Rotated logs

## Performance Impact

The logging system is designed for minimal performance impact:

- JSON serialization: ~0.1ms per log entry
- File I/O: Buffered, async where possible
- Rotation: Happens in background
- Log level filtering: Fast early exit

In production:
- Use INFO level for most components
- Use DEBUG level only for debugging
- Avoid TRACE level unless absolutely necessary

## Maintenance

### Log Cleanup

Logs are automatically rotated and archived. Manual cleanup:

```bash
# Remove old archives (>30 days)
find trace/archived -mtime +30 -delete

# Clear all logs (development only!)
find trace/logs -name "*.log" -delete
```

### Disk Space Monitoring

Each component's main log rotates at 100MB with 10 backups = max 1GB per component.

For high-traffic components, consider:
- Reducing backup count
- More frequent rotation
- Moving archives to cold storage

## Troubleshooting

### Logs Not Appearing

Check:
1. Logger level is set appropriately
2. `trace/logs/` directory exists and is writable
3. No permission errors

### Invalid JSON in Logs

This shouldn't happen, but if it does:
1. Check for custom data serialization issues
2. Verify no print() statements are interfering
3. Review recent code changes

### Performance Issues

If logging is slow:
1. Check log level (reduce to INFO in production)
2. Verify disk I/O is not bottlenecked
3. Consider async logging for high-throughput components

## Summary

The trace logging system provides comprehensive debugging capabilities through:

✓ **Structured JSON logs** - Easy parsing and analysis
✓ **No console output** - All logs persisted to files
✓ **Automatic rotation** - Size and time-based
✓ **Request tracing** - Follow requests through pipeline
✓ **Performance tracking** - Automatic timing and metrics
✓ **Error logging** - Full stack traces
✓ **Analysis tools** - Find errors, trace requests, analyze performance
✓ **Component isolation** - Separate logs per component
✓ **Context propagation** - Request/user/session tracking

This ensures that every issue can be debugged by:
1. Finding the request ID
2. Tracing it through the logs
3. Identifying the root cause
4. Fixing the issue with confidence
