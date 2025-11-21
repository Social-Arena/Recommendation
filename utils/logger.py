"""
Simple logger wrapper for Recommendation module
"""

import logging
from pathlib import Path


# Simple logger cache
_loggers = {}


def get_logger(name: str, component: str = "recommendation") -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
        component: Component name
        
    Returns:
        Logger instance
    """
    key = f"{component}.{name}"
    
    if key not in _loggers:
        logger = logging.getLogger(key)
        logger.setLevel(logging.INFO)
        
        # Create trace directory if needed
        trace_dir = Path("trace") / component
        trace_dir.mkdir(parents=True, exist_ok=True)
        
        # Add file handler
        log_file = trace_dir / f"{name}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Simple format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        _loggers[key] = logger
    
    return _loggers[key]
