"""
Logging decorators for automatic performance and error tracking.

These decorators can be applied to functions and methods to automatically
log execution details, performance metrics, and errors.
"""

import functools
import time
import asyncio
import inspect
from typing import Callable, Any, Optional
from .logger import get_logger, get_performance_logger, get_error_logger


def log_performance(logger=None, component: str = "performance", log_args: bool = True, log_result: bool = False):
    """
    Decorator to log function performance metrics.

    Args:
        logger: Logger instance (if None, creates a performance logger)
        component: Component name for logging
        log_args: Whether to log function arguments
        log_result: Whether to log function result

    Usage:
        @log_performance()
        def my_function(arg1, arg2):
            return result
    """

    def decorator(func: Callable) -> Callable:
        perf_logger = logger or get_performance_logger()
        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            module_name = func.__module__

            # Prepare log data
            extra_data = {
                "function": function_name,
                "module_name": module_name,
                "type": "async"
            }

            # Log arguments if requested
            if log_args:
                try:
                    # Get function signature
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    # Filter out sensitive data and large objects
                    safe_args = {}
                    for key, value in bound_args.arguments.items():
                        if key in ['password', 'token', 'secret', 'api_key']:
                            safe_args[key] = "***REDACTED***"
                        elif isinstance(value, (str, int, float, bool, type(None))):
                            safe_args[key] = value
                        else:
                            safe_args[key] = f"<{type(value).__name__}>"

                    extra_data["arguments"] = safe_args
                except Exception:
                    extra_data["arguments"] = "<error_binding_args>"

            # Execute function
            error = None
            result = None
            try:
                perf_logger.debug(f"Starting {function_name}", extra=extra_data)
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                # Calculate duration
                duration_ms = (time.time() - start_time) * 1000

                # Prepare final log data
                final_data = {
                    **extra_data,
                    "duration_ms": round(duration_ms, 2),
                    "status": "error" if error else "success"
                }

                # Log result if requested and no error
                if log_result and result is not None and not error:
                    if isinstance(result, (str, int, float, bool, list, dict)):
                        final_data["result"] = result
                    else:
                        final_data["result_type"] = type(result).__name__

                # Log error if present
                if error:
                    final_data["error_type"] = type(error).__name__
                    final_data["error_message"] = str(error)
                    perf_logger.error(
                        f"{function_name} failed after {duration_ms:.2f}ms",
                        extra=final_data
                    )
                else:
                    perf_logger.info(
                        f"{function_name} completed in {duration_ms:.2f}ms",
                        extra=final_data
                    )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            function_name = func.__name__
            module_name = func.__module__

            # Prepare log data
            extra_data = {
                "function": function_name,
                "module_name": module_name,
                "type": "sync"
            }

            # Log arguments if requested
            if log_args:
                try:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()

                    safe_args = {}
                    for key, value in bound_args.arguments.items():
                        if key in ['password', 'token', 'secret', 'api_key']:
                            safe_args[key] = "***REDACTED***"
                        elif isinstance(value, (str, int, float, bool, type(None))):
                            safe_args[key] = value
                        else:
                            safe_args[key] = f"<{type(value).__name__}>"

                    extra_data["arguments"] = safe_args
                except Exception:
                    extra_data["arguments"] = "<error_binding_args>"

            # Execute function
            error = None
            result = None
            try:
                perf_logger.debug(f"Starting {function_name}", extra=extra_data)
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = e
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                final_data = {
                    **extra_data,
                    "duration_ms": round(duration_ms, 2),
                    "status": "error" if error else "success"
                }

                if log_result and result is not None and not error:
                    if isinstance(result, (str, int, float, bool, list, dict)):
                        final_data["result"] = result
                    else:
                        final_data["result_type"] = type(result).__name__

                if error:
                    final_data["error_type"] = type(error).__name__
                    final_data["error_message"] = str(error)
                    perf_logger.error(
                        f"{function_name} failed after {duration_ms:.2f}ms",
                        extra=final_data
                    )
                else:
                    perf_logger.info(
                        f"{function_name} completed in {duration_ms:.2f}ms",
                        extra=final_data
                    )

        return async_wrapper if is_async else sync_wrapper

    return decorator


def log_errors(logger=None, component: str = "errors", reraise: bool = True, default_return: Any = None):
    """
    Decorator to log errors with full stack traces.

    Args:
        logger: Logger instance (if None, creates an error logger)
        component: Component name for logging
        reraise: Whether to re-raise the exception after logging
        default_return: Default value to return if exception occurs and reraise=False

    Usage:
        @log_errors(reraise=True)
        def my_function():
            raise ValueError("Something went wrong")
    """

    def decorator(func: Callable) -> Callable:
        err_logger = logger or get_error_logger()
        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Prepare error log data
                extra_data = {
                    "function": func.__name__,
                    "module_name": func.__module__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "type": "async"
                }

                # Try to get arguments
                try:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    safe_args = {
                        k: "***REDACTED***" if k in ['password', 'token', 'secret'] else str(v)[:100]
                        for k, v in bound_args.arguments.items()
                    }
                    extra_data["arguments"] = safe_args
                except Exception:
                    extra_data["arguments"] = "<error_binding_args>"

                # Log the error with stack trace
                err_logger.error(
                    f"Error in {func.__name__}: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                    extra=extra_data,
                    stack_info=True
                )

                if reraise:
                    raise
                else:
                    return default_return

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                extra_data = {
                    "function": func.__name__,
                    "module_name": func.__module__,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "type": "sync"
                }

                try:
                    sig = inspect.signature(func)
                    bound_args = sig.bind(*args, **kwargs)
                    safe_args = {
                        k: "***REDACTED***" if k in ['password', 'token', 'secret'] else str(v)[:100]
                        for k, v in bound_args.arguments.items()
                    }
                    extra_data["arguments"] = safe_args
                except Exception:
                    extra_data["arguments"] = "<error_binding_args>"

                err_logger.error(
                    f"Error in {func.__name__}: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                    extra=extra_data,
                    stack_info=True
                )

                if reraise:
                    raise
                else:
                    return default_return

        return async_wrapper if is_async else sync_wrapper

    return decorator


def log_entry_exit(logger=None, component: str = "app"):
    """
    Decorator to log function entry and exit.

    Args:
        logger: Logger instance
        component: Component name for logging

    Usage:
        @log_entry_exit()
        def my_function(arg1, arg2):
            return result
    """

    def decorator(func: Callable) -> Callable:
        func_logger = logger or get_logger(func.__module__, component=component)
        is_async = asyncio.iscoroutinefunction(func)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_logger.debug(
                f"Entering {func.__name__}",
                extra={"function": func.__name__, "module_name": func.__module__}
            )
            try:
                result = await func(*args, **kwargs)
                func_logger.debug(
                    f"Exiting {func.__name__}",
                    extra={"function": func.__name__, "module_name": func.__module__}
                )
                return result
            except Exception as e:
                func_logger.debug(
                    f"Exiting {func.__name__} with exception",
                    extra={
                        "function": func.__name__,
                        "module_name": func.__module__,
                        "exception": type(e).__name__
                    }
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_logger.debug(
                f"Entering {func.__name__}",
                extra={"function": func.__name__, "module_name": func.__module__}
            )
            try:
                result = func(*args, **kwargs)
                func_logger.debug(
                    f"Exiting {func.__name__}",
                    extra={"function": func.__name__, "module_name": func.__module__}
                )
                return result
            except Exception as e:
                func_logger.debug(
                    f"Exiting {func.__name__} with exception",
                    extra={
                        "function": func.__name__,
                        "module_name": func.__module__,
                        "exception": type(e).__name__
                    }
                )
                raise

        return async_wrapper if is_async else sync_wrapper

    return decorator


def trace_execution(logger=None, component: str = "app"):
    """
    Decorator for detailed execution tracing.

    Combines performance logging, error logging, and entry/exit logging.

    Usage:
        @trace_execution(component="candidate")
        async def generate_candidates(user_id: str):
            # Function is fully traced
            pass
    """

    def decorator(func: Callable) -> Callable:
        # Stack decorators
        decorated_func = log_entry_exit(logger, component)(func)
        decorated_func = log_errors(logger, component)(decorated_func)
        decorated_func = log_performance(logger, component)(decorated_func)
        return decorated_func

    return decorator


__all__ = [
    'log_performance',
    'log_errors',
    'log_entry_exit',
    'trace_execution'
]
