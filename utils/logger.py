"""
Unified logging system for Twitter Recommendation Engine.

All components use this logger to ensure consistent, structured logging
to files for debugging and analysis.
"""

import logging
import json
import os
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import threading

# Thread-local storage for request context
_context = threading.local()


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs in JSON format."""

    def __init__(self):
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""

        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
            "context": {
                "function": record.funcName,
                "file": record.filename,
                "line": record.lineno,
                "thread": record.thread,
                "process": record.process
            }
        }

        # Add request context if available
        if hasattr(_context, 'request_id'):
            log_data["request_id"] = _context.request_id
        if hasattr(_context, 'user_id'):
            log_data["user_id"] = _context.user_id
        if hasattr(_context, 'session_id'):
            log_data["session_id"] = _context.session_id

        # Add extra data from the log record
        if hasattr(record, 'extra_data'):
            log_data["data"] = record.extra_data

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }

        # Add stack trace for errors
        if record.levelno >= logging.ERROR and record.stack_info:
            log_data["stack_trace"] = record.stack_info

        return json.dumps(log_data, default=str, ensure_ascii=False)


class ContextAdapter(logging.LoggerAdapter):
    """Adapter that adds context to log messages."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Add extra data to the log record."""
        extra = kwargs.get('extra', {})

        # Extract extra data and store it separately
        if extra:
            # Create a new LogRecord attribute for extra data
            kwargs['extra'] = kwargs.get('extra', {})
            kwargs['extra']['extra_data'] = extra.copy()

        return msg, kwargs


def get_logger(name: str, component: str = "app", level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)
        component: Component name (app, candidate, ranking, etc.)
        level: Log level (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Set log level
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Prevent propagation to root logger (no console output)
    logger.propagate = False

    # Create trace directory if it doesn't exist
    trace_dir = Path(__file__).parent.parent / "trace" / "logs" / component
    trace_dir.mkdir(parents=True, exist_ok=True)

    # Main log file (rotated by size)
    main_log_file = trace_dir / f"{component}.log"
    main_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=100 * 1024 * 1024,  # 100MB
        backupCount=10,
        encoding='utf-8'
    )
    main_handler.setFormatter(JSONFormatter())
    main_handler.setLevel(logging.DEBUG)
    logger.addHandler(main_handler)

    # Error log file (errors only)
    error_log_file = Path(__file__).parent.parent / "trace" / "logs" / "errors" / f"{component}_errors.log"
    error_log_file.parent.mkdir(parents=True, exist_ok=True)
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setFormatter(JSONFormatter())
    error_handler.setLevel(logging.ERROR)
    logger.addHandler(error_handler)

    # Daily rotating file for time-series analysis
    daily_log_file = trace_dir / f"{component}_daily.log"
    daily_handler = TimedRotatingFileHandler(
        daily_log_file,
        when='midnight',
        interval=1,
        backupCount=30,  # Keep 30 days
        encoding='utf-8'
    )
    daily_handler.setFormatter(JSONFormatter())
    daily_handler.setLevel(logging.INFO)
    logger.addHandler(daily_handler)

    return logger


class LogContext:
    """Context manager for setting request-specific logging context."""

    def __init__(self, request_id: Optional[str] = None,
                 user_id: Optional[str] = None,
                 session_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self.session_id = session_id
        self.previous_context = {}

    def __enter__(self):
        """Set context on enter."""
        # Save previous context
        self.previous_context = {
            'request_id': getattr(_context, 'request_id', None),
            'user_id': getattr(_context, 'user_id', None),
            'session_id': getattr(_context, 'session_id', None)
        }

        # Set new context
        if self.request_id:
            _context.request_id = self.request_id
        if self.user_id:
            _context.user_id = self.user_id
        if self.session_id:
            _context.session_id = self.session_id

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore previous context on exit."""
        for key, value in self.previous_context.items():
            if value is not None:
                setattr(_context, key, value)
            elif hasattr(_context, key):
                delattr(_context, key)


def set_log_context(request_id: Optional[str] = None,
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None):
    """
    Set logging context for the current thread.

    Args:
        request_id: Unique request identifier
        user_id: User identifier
        session_id: Session identifier
    """
    if request_id:
        _context.request_id = request_id
    if user_id:
        _context.user_id = user_id
    if session_id:
        _context.session_id = session_id


def clear_log_context():
    """Clear logging context for the current thread."""
    for attr in ['request_id', 'user_id', 'session_id']:
        if hasattr(_context, attr):
            delattr(_context, attr)


# Add custom TRACE level
TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")


def trace(self, message: str, *args, **kwargs):
    """Log a message with TRACE level."""
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


# Add trace method to Logger class
logging.Logger.trace = trace


# Performance tracking logger
def get_performance_logger() -> logging.Logger:
    """Get logger specifically for performance metrics."""
    logger = get_logger("performance", component="performance", level="INFO")
    return logger


# Error tracking logger
def get_error_logger() -> logging.Logger:
    """Get logger specifically for error tracking."""
    logger = get_logger("errors", component="errors", level="ERROR")
    return logger


# Export commonly used items
__all__ = [
    'get_logger',
    'LogContext',
    'set_log_context',
    'clear_log_context',
    'get_performance_logger',
    'get_error_logger',
    'TRACE_LEVEL'
]
