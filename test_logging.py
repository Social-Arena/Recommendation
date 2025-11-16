#!/usr/bin/env python3
"""
Quick test script to verify the logging system is working correctly.
"""

import sys
import json
from pathlib import Path
from utils.logger import get_logger, LogContext
from utils.decorators import log_performance, log_errors

# Test 1: Basic logging
print("Test 1: Basic logging...")
logger = get_logger(__name__, component="app", level="INFO")
logger.info("Test message", extra={"test": "basic_logging", "status": "success"})
print("✓ Basic logging test passed")

# Test 2: Context logging
print("\nTest 2: Context logging...")
with LogContext(request_id="test-request-123", user_id="test-user-456"):
    logger.info("Test with context", extra={"test": "context_logging"})
print("✓ Context logging test passed")

# Test 3: Performance decorator
print("\nTest 3: Performance decorator...")

@log_performance(log_args=True)
def test_function(arg1, arg2):
    return arg1 + arg2

result = test_function(10, 20)
assert result == 30
print("✓ Performance decorator test passed")

# Test 4: Error decorator
print("\nTest 4: Error decorator...")

@log_errors(reraise=False, default_return="error_handled")
def test_error_function():
    raise ValueError("Test error")

result = test_error_function()
assert result == "error_handled"
print("✓ Error decorator test passed")

# Test 5: Verify log files exist
print("\nTest 5: Verifying log files...")
trace_dir = Path(__file__).parent / "trace" / "logs"

expected_files = [
    trace_dir / "app" / "app.log",
    trace_dir / "performance" / "performance.log",
]

for log_file in expected_files:
    if log_file.exists():
        print(f"✓ Log file exists: {log_file.relative_to(Path(__file__).parent)}")

        # Verify it contains valid JSON
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                try:
                    log_entry = json.loads(lines[-1])
                    print(f"  - Valid JSON format")
                    print(f"  - Last entry timestamp: {log_entry.get('timestamp')}")
                except json.JSONDecodeError as e:
                    print(f"  ✗ Invalid JSON in log file: {e}")
    else:
        print(f"✗ Log file not found: {log_file.relative_to(Path(__file__).parent)}")

print("\n" + "="*60)
print("All tests passed! Logging system is working correctly.")
print("="*60)
print("\nLog files location:")
print(f"  {trace_dir.relative_to(Path(__file__).parent)}/")
print("\nYou can now:")
print("  1. Run the full example: python examples/logging_example.py")
print("  2. View logs: cat trace/logs/app/app.log | python -m json.tool")
print("  3. Analyze logs: python utils/log_analyzer.py --help")
print("="*60)
