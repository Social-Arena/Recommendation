"""
Utility modules for Twitter Recommendation Engine.

This package provides:
- Structured logging system
- Performance tracking decorators
- Log analysis tools
- Request tracing utilities
"""

from .logger import (
    get_logger,
    LogContext,
    set_log_context,
    clear_log_context,
    get_performance_logger,
    get_error_logger,
    TRACE_LEVEL
)

from .decorators import (
    log_performance,
    log_errors,
    log_entry_exit,
    trace_execution
)

from .log_analyzer import LogAnalyzer
from .trace_request import RequestTracer

__all__ = [
    # Logger functions
    'get_logger',
    'LogContext',
    'set_log_context',
    'clear_log_context',
    'get_performance_logger',
    'get_error_logger',
    'TRACE_LEVEL',

    # Decorators
    'log_performance',
    'log_errors',
    'log_entry_exit',
    'trace_execution',

    # Analysis tools
    'LogAnalyzer',
    'RequestTracer',
]

__version__ = '1.0.0'
