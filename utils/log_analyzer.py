"""
Log analysis tools for debugging and troubleshooting.

Provides utilities to analyze logs, find errors, trace requests,
and identify performance issues.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re


class LogAnalyzer:
    """Analyzer for structured JSON logs."""

    def __init__(self, trace_dir: str = None):
        """
        Initialize log analyzer.

        Args:
            trace_dir: Path to trace directory (default: ../trace/logs)
        """
        if trace_dir is None:
            current_dir = Path(__file__).parent.parent
            trace_dir = current_dir / "trace" / "logs"
        self.trace_dir = Path(trace_dir)

    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a JSON log line."""
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            return None

    def read_logs(self, component: str, log_type: str = "main") -> List[Dict[str, Any]]:
        """
        Read logs from a specific component.

        Args:
            component: Component name (app, candidate, ranking, etc.)
            log_type: Type of log (main, errors, daily)

        Returns:
            List of parsed log entries
        """
        if log_type == "main":
            log_file = self.trace_dir / component / f"{component}.log"
        elif log_type == "errors":
            log_file = self.trace_dir / "errors" / f"{component}_errors.log"
        elif log_type == "daily":
            log_file = self.trace_dir / component / f"{component}_daily.log"
        else:
            raise ValueError(f"Unknown log type: {log_type}")

        if not log_file.exists():
            print(f"Warning: Log file not found: {log_file}")
            return []

        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                log_entry = self.parse_log_line(line)
                if log_entry:
                    logs.append(log_entry)

        return logs

    def find_errors(self, component: str = None, since: datetime = None,
                   error_type: str = None) -> List[Dict[str, Any]]:
        """
        Find error logs matching criteria.

        Args:
            component: Component name (if None, search all components)
            since: Only errors after this timestamp
            error_type: Filter by exception type

        Returns:
            List of error log entries
        """
        errors = []

        if component:
            components = [component]
        else:
            # Search all components
            error_dir = self.trace_dir / "errors"
            if error_dir.exists():
                components = [
                    f.stem.replace('_errors', '')
                    for f in error_dir.glob("*_errors.log")
                ]
            else:
                components = []

        for comp in components:
            comp_errors = self.read_logs(comp, log_type="errors")

            for error in comp_errors:
                # Filter by timestamp
                if since:
                    try:
                        error_time = datetime.fromisoformat(error['timestamp'].rstrip('Z'))
                        if error_time < since:
                            continue
                    except (KeyError, ValueError):
                        continue

                # Filter by error type
                if error_type:
                    try:
                        if error.get('exception', {}).get('type') != error_type:
                            continue
                    except (KeyError, AttributeError):
                        continue

                errors.append(error)

        return errors

    def trace_request(self, request_id: str) -> List[Dict[str, Any]]:
        """
        Trace all logs for a specific request.

        Args:
            request_id: Request ID to trace

        Returns:
            List of log entries for this request, sorted by timestamp
        """
        request_logs = []

        # Search all component logs
        for component_dir in self.trace_dir.iterdir():
            if not component_dir.is_dir():
                continue

            for log_file in component_dir.glob("*.log"):
                if not log_file.is_file():
                    continue

                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        log_entry = self.parse_log_line(line)
                        if log_entry and log_entry.get('request_id') == request_id:
                            request_logs.append(log_entry)

        # Sort by timestamp
        request_logs.sort(key=lambda x: x.get('timestamp', ''))

        return request_logs

    def trace_user(self, user_id: str, since: datetime = None,
                  until: datetime = None) -> List[Dict[str, Any]]:
        """
        Trace all logs for a specific user.

        Args:
            user_id: User ID to trace
            since: Start timestamp
            until: End timestamp

        Returns:
            List of log entries for this user, sorted by timestamp
        """
        user_logs = []

        # Search all component logs
        for component_dir in self.trace_dir.iterdir():
            if not component_dir.is_dir():
                continue

            for log_file in component_dir.glob("*.log"):
                if not log_file.is_file():
                    continue

                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        log_entry = self.parse_log_line(line)
                        if not log_entry or log_entry.get('user_id') != user_id:
                            continue

                        # Filter by timestamp
                        try:
                            log_time = datetime.fromisoformat(log_entry['timestamp'].rstrip('Z'))
                            if since and log_time < since:
                                continue
                            if until and log_time > until:
                                continue
                        except (KeyError, ValueError):
                            pass

                        user_logs.append(log_entry)

        # Sort by timestamp
        user_logs.sort(key=lambda x: x.get('timestamp', ''))

        return user_logs

    def analyze_performance(self, component: str,
                          since: datetime = None) -> Dict[str, Any]:
        """
        Analyze performance metrics for a component.

        Args:
            component: Component name
            since: Only analyze logs after this timestamp

        Returns:
            Performance statistics
        """
        perf_logs = self.read_logs("performance")

        # Filter by component and timestamp
        filtered_logs = []
        for log in perf_logs:
            # Check component
            if log.get('component') != component and \
               log.get('data', {}).get('module', '').find(component) == -1:
                continue

            # Check timestamp
            if since:
                try:
                    log_time = datetime.fromisoformat(log['timestamp'].rstrip('Z'))
                    if log_time < since:
                        continue
                except (KeyError, ValueError):
                    continue

            filtered_logs.append(log)

        if not filtered_logs:
            return {
                "total_calls": 0,
                "message": "No performance data found"
            }

        # Extract durations
        durations = []
        function_stats = defaultdict(list)
        error_count = 0

        for log in filtered_logs:
            duration = log.get('data', {}).get('duration_ms')
            if duration is not None:
                durations.append(duration)

                function_name = log.get('data', {}).get('function', 'unknown')
                function_stats[function_name].append(duration)

                if log.get('data', {}).get('status') == 'error':
                    error_count += 1

        # Calculate statistics
        durations.sort()
        n = len(durations)

        stats = {
            "total_calls": n,
            "error_count": error_count,
            "error_rate": error_count / n if n > 0 else 0,
            "duration_ms": {
                "min": durations[0] if durations else 0,
                "max": durations[-1] if durations else 0,
                "mean": sum(durations) / n if n > 0 else 0,
                "median": durations[n // 2] if durations else 0,
                "p95": durations[int(n * 0.95)] if durations else 0,
                "p99": durations[int(n * 0.99)] if durations else 0
            },
            "by_function": {}
        }

        # Per-function statistics
        for func_name, func_durations in function_stats.items():
            func_durations.sort()
            fn = len(func_durations)
            stats["by_function"][func_name] = {
                "calls": fn,
                "mean": sum(func_durations) / fn,
                "median": func_durations[fn // 2],
                "p95": func_durations[int(fn * 0.95)] if fn > 0 else 0
            }

        return stats

    def find_slow_operations(self, component: str, threshold_ms: float = 1000,
                           since: datetime = None) -> List[Dict[str, Any]]:
        """
        Find operations slower than threshold.

        Args:
            component: Component name
            threshold_ms: Threshold in milliseconds
            since: Only analyze logs after this timestamp

        Returns:
            List of slow operations
        """
        perf_logs = self.read_logs("performance")

        slow_ops = []
        for log in perf_logs:
            # Check timestamp
            if since:
                try:
                    log_time = datetime.fromisoformat(log['timestamp'].rstrip('Z'))
                    if log_time < since:
                        continue
                except (KeyError, ValueError):
                    continue

            # Check duration
            duration = log.get('data', {}).get('duration_ms')
            if duration and duration > threshold_ms:
                slow_ops.append({
                    "timestamp": log.get('timestamp'),
                    "component": log.get('component'),
                    "function": log.get('data', {}).get('function'),
                    "duration_ms": duration,
                    "request_id": log.get('request_id'),
                    "user_id": log.get('user_id'),
                    "arguments": log.get('data', {}).get('arguments')
                })

        # Sort by duration (slowest first)
        slow_ops.sort(key=lambda x: x['duration_ms'], reverse=True)

        return slow_ops

    def summarize_errors(self, since: datetime = None) -> Dict[str, Any]:
        """
        Summarize all errors.

        Args:
            since: Only analyze errors after this timestamp

        Returns:
            Error summary
        """
        errors = self.find_errors(since=since)

        if not errors:
            return {
                "total_errors": 0,
                "message": "No errors found"
            }

        # Count by type
        error_types = Counter()
        error_components = Counter()
        error_functions = Counter()

        for error in errors:
            error_type = error.get('exception', {}).get('type', 'Unknown')
            component = error.get('component', 'Unknown')
            function = error.get('context', {}).get('function', 'Unknown')

            error_types[error_type] += 1
            error_components[component] += 1
            error_functions[function] += 1

        return {
            "total_errors": len(errors),
            "by_type": dict(error_types.most_common(10)),
            "by_component": dict(error_components.most_common(10)),
            "by_function": dict(error_functions.most_common(10)),
            "recent_errors": errors[-10:]  # Last 10 errors
        }

    def export_trace(self, request_id: str, output_file: str):
        """
        Export request trace to a file.

        Args:
            request_id: Request ID to trace
            output_file: Output file path
        """
        logs = self.trace_request(request_id)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                "request_id": request_id,
                "total_entries": len(logs),
                "trace": logs
            }, f, indent=2, default=str)

        print(f"Trace exported to {output_file}")

    def print_trace(self, request_id: str):
        """Print request trace in readable format."""
        logs = self.trace_request(request_id)

        if not logs:
            print(f"No logs found for request_id: {request_id}")
            return

        print(f"\n{'='*80}")
        print(f"Request Trace: {request_id}")
        print(f"Total Entries: {len(logs)}")
        print(f"{'='*80}\n")

        for i, log in enumerate(logs, 1):
            timestamp = log.get('timestamp', 'N/A')
            level = log.get('level', 'INFO')
            component = log.get('component', 'Unknown')
            message = log.get('message', '')
            function = log.get('context', {}).get('function', 'N/A')

            print(f"{i}. [{timestamp}] [{level}] {component}::{function}")
            print(f"   {message}")

            if log.get('data'):
                print(f"   Data: {json.dumps(log['data'], indent=6)}")

            if log.get('exception'):
                print(f"   Exception: {log['exception']['type']}: {log['exception']['message']}")

            print()


def main():
    """CLI interface for log analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze recommendation engine logs")
    parser.add_argument('--trace-dir', help="Path to trace directory")

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Trace request
    trace_parser = subparsers.add_parser('trace', help='Trace a request')
    trace_parser.add_argument('request_id', help='Request ID to trace')
    trace_parser.add_argument('--export', help='Export to file')

    # Find errors
    error_parser = subparsers.add_parser('errors', help='Find errors')
    error_parser.add_argument('--component', help='Component name')
    error_parser.add_argument('--type', help='Error type')
    error_parser.add_argument('--since', help='Since timestamp (ISO format)')

    # Performance analysis
    perf_parser = subparsers.add_parser('performance', help='Analyze performance')
    perf_parser.add_argument('component', help='Component name')
    perf_parser.add_argument('--since', help='Since timestamp (ISO format)')

    # Slow operations
    slow_parser = subparsers.add_parser('slow', help='Find slow operations')
    slow_parser.add_argument('component', help='Component name')
    slow_parser.add_argument('--threshold', type=float, default=1000,
                            help='Threshold in milliseconds')

    args = parser.parse_args()

    analyzer = LogAnalyzer(args.trace_dir)

    if args.command == 'trace':
        if args.export:
            analyzer.export_trace(args.request_id, args.export)
        else:
            analyzer.print_trace(args.request_id)

    elif args.command == 'errors':
        since = datetime.fromisoformat(args.since) if args.since else None
        errors = analyzer.find_errors(
            component=args.component,
            since=since,
            error_type=args.type
        )
        print(json.dumps(errors, indent=2, default=str))

    elif args.command == 'performance':
        since = datetime.fromisoformat(args.since) if args.since else None
        stats = analyzer.analyze_performance(args.component, since=since)
        print(json.dumps(stats, indent=2))

    elif args.command == 'slow':
        slow_ops = analyzer.find_slow_operations(
            args.component,
            threshold_ms=args.threshold
        )
        print(json.dumps(slow_ops, indent=2, default=str))


if __name__ == '__main__':
    main()
