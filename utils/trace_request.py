"""
Request tracing utility for debugging recommendation pipeline.

This tool traces a request through all stages of the recommendation
pipeline, showing timing, data flow, and any errors.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .log_analyzer import LogAnalyzer


class RequestTracer:
    """Trace requests through the recommendation pipeline."""

    def __init__(self, trace_dir: str = None):
        """Initialize request tracer."""
        self.analyzer = LogAnalyzer(trace_dir)

    def trace_recommendation_flow(self, request_id: str) -> Dict[str, Any]:
        """
        Trace a recommendation request through the pipeline.

        Args:
            request_id: Request ID to trace

        Returns:
            Structured trace showing pipeline stages
        """
        logs = self.analyzer.trace_request(request_id)

        if not logs:
            return {
                "request_id": request_id,
                "status": "not_found",
                "message": "No logs found for this request"
            }

        # Organize by pipeline stage
        stages = {
            "candidate_generation": [],
            "light_ranking": [],
            "heavy_ranking": [],
            "exploration": [],
            "diversity": [],
            "safety_filter": [],
            "serving": [],
            "other": []
        }

        errors = []
        performance_metrics = {}

        for log in logs:
            component = log.get('component', '')
            message = log.get('message', '')

            # Categorize by pipeline stage
            if 'candidate' in component.lower() or 'candidate' in message.lower():
                stages['candidate_generation'].append(log)
            elif 'light' in message.lower() and 'rank' in message.lower():
                stages['light_ranking'].append(log)
            elif 'heavy' in message.lower() and 'rank' in message.lower():
                stages['heavy_ranking'].append(log)
            elif 'exploration' in component.lower() or 'exploration' in message.lower():
                stages['exploration'].append(log)
            elif 'diversity' in component.lower() or 'diversity' in message.lower():
                stages['diversity'].append(log)
            elif 'safety' in component.lower() or 'filter' in message.lower():
                stages['safety_filter'].append(log)
            elif 'serving' in component.lower() or 'recommendation' in message.lower():
                stages['serving'].append(log)
            else:
                stages['other'].append(log)

            # Collect errors
            if log.get('level') in ['ERROR', 'CRITICAL']:
                errors.append(log)

            # Collect performance metrics
            if log.get('data', {}).get('duration_ms'):
                function = log.get('data', {}).get('function', 'unknown')
                duration = log['data']['duration_ms']
                if function not in performance_metrics:
                    performance_metrics[function] = []
                performance_metrics[function].append(duration)

        # Calculate summary
        start_time = logs[0].get('timestamp') if logs else None
        end_time = logs[-1].get('timestamp') if logs else None

        total_duration = None
        if start_time and end_time:
            try:
                start = datetime.fromisoformat(start_time.rstrip('Z'))
                end = datetime.fromisoformat(end_time.rstrip('Z'))
                total_duration = (end - start).total_seconds() * 1000
            except ValueError:
                pass

        # Build stage summaries
        stage_summaries = {}
        for stage_name, stage_logs in stages.items():
            if not stage_logs:
                continue

            stage_summaries[stage_name] = {
                "log_count": len(stage_logs),
                "duration_ms": sum(
                    log.get('data', {}).get('duration_ms', 0)
                    for log in stage_logs
                ),
                "errors": [log for log in stage_logs if log.get('level') in ['ERROR', 'CRITICAL']],
                "key_events": [
                    {
                        "timestamp": log.get('timestamp'),
                        "message": log.get('message'),
                        "data": log.get('data')
                    }
                    for log in stage_logs
                    if log.get('level') in ['INFO', 'WARNING', 'ERROR']
                ]
            }

        return {
            "request_id": request_id,
            "status": "error" if errors else "success",
            "total_duration_ms": total_duration,
            "start_time": start_time,
            "end_time": end_time,
            "total_logs": len(logs),
            "error_count": len(errors),
            "stages": stage_summaries,
            "errors": errors,
            "performance": {
                func: {
                    "calls": len(durations),
                    "total_ms": sum(durations),
                    "mean_ms": sum(durations) / len(durations),
                    "max_ms": max(durations)
                }
                for func, durations in performance_metrics.items()
            }
        }

    def print_recommendation_flow(self, request_id: str):
        """Print recommendation flow in readable format."""
        trace = self.trace_recommendation_flow(request_id)

        print(f"\n{'='*80}")
        print(f"Recommendation Pipeline Trace")
        print(f"{'='*80}")
        print(f"Request ID: {trace['request_id']}")
        print(f"Status: {trace['status'].upper()}")
        print(f"Total Duration: {trace.get('total_duration_ms', 'N/A')} ms")
        print(f"Total Logs: {trace['total_logs']}")
        print(f"Errors: {trace['error_count']}")
        print(f"{'='*80}\n")

        # Print stage summaries
        print("Pipeline Stages:")
        print("-" * 80)

        stage_order = [
            "candidate_generation",
            "light_ranking",
            "heavy_ranking",
            "exploration",
            "diversity",
            "safety_filter",
            "serving"
        ]

        for i, stage_name in enumerate(stage_order, 1):
            if stage_name not in trace['stages']:
                continue

            stage = trace['stages'][stage_name]
            print(f"\n{i}. {stage_name.replace('_', ' ').title()}")
            print(f"   Logs: {stage['log_count']}")
            print(f"   Duration: {stage['duration_ms']:.2f} ms")

            if stage['errors']:
                print(f"   ❌ Errors: {len(stage['errors'])}")

            if stage['key_events']:
                print(f"   Key Events:")
                for event in stage['key_events'][:3]:  # Show top 3 events
                    print(f"     • {event['message']}")
                    if event.get('data'):
                        for key, value in list(event['data'].items())[:2]:
                            print(f"       - {key}: {value}")

        # Print errors if any
        if trace['errors']:
            print(f"\n{'='*80}")
            print("Errors:")
            print("-" * 80)

            for error in trace['errors']:
                print(f"\n❌ {error.get('message')}")
                print(f"   Component: {error.get('component')}")
                print(f"   Timestamp: {error.get('timestamp')}")

                if error.get('exception'):
                    exc = error['exception']
                    print(f"   Exception: {exc.get('type')}: {exc.get('message')}")

        # Print performance summary
        if trace['performance']:
            print(f"\n{'='*80}")
            print("Performance Summary:")
            print("-" * 80)

            perf_items = sorted(
                trace['performance'].items(),
                key=lambda x: x[1]['total_ms'],
                reverse=True
            )

            for func, metrics in perf_items[:10]:  # Top 10
                print(f"\n{func}:")
                print(f"   Calls: {metrics['calls']}")
                print(f"   Total: {metrics['total_ms']:.2f} ms")
                print(f"   Mean: {metrics['mean_ms']:.2f} ms")
                print(f"   Max: {metrics['max_ms']:.2f} ms")

        print(f"\n{'='*80}\n")

    def compare_requests(self, request_id1: str, request_id2: str) -> Dict[str, Any]:
        """
        Compare two requests to identify differences.

        Args:
            request_id1: First request ID
            request_id2: Second request ID

        Returns:
            Comparison results
        """
        trace1 = self.trace_recommendation_flow(request_id1)
        trace2 = self.trace_recommendation_flow(request_id2)

        comparison = {
            "request_1": request_id1,
            "request_2": request_id2,
            "status_comparison": {
                "request_1": trace1.get('status'),
                "request_2": trace2.get('status')
            },
            "duration_comparison": {
                "request_1": trace1.get('total_duration_ms'),
                "request_2": trace2.get('total_duration_ms'),
                "difference_ms": (
                    trace1.get('total_duration_ms', 0) -
                    trace2.get('total_duration_ms', 0)
                ) if trace1.get('total_duration_ms') and trace2.get('total_duration_ms') else None
            },
            "error_comparison": {
                "request_1": trace1.get('error_count', 0),
                "request_2": trace2.get('error_count', 0)
            },
            "stage_comparison": {}
        }

        # Compare stages
        all_stages = set(trace1.get('stages', {}).keys()) | set(trace2.get('stages', {}).keys())

        for stage in all_stages:
            stage1 = trace1.get('stages', {}).get(stage, {})
            stage2 = trace2.get('stages', {}).get(stage, {})

            comparison["stage_comparison"][stage] = {
                "duration_difference_ms": (
                    stage1.get('duration_ms', 0) - stage2.get('duration_ms', 0)
                ),
                "log_count_difference": (
                    stage1.get('log_count', 0) - stage2.get('log_count', 0)
                )
            }

        return comparison


def main():
    """CLI interface for request tracer."""
    import argparse

    parser = argparse.ArgumentParser(description="Trace recommendation requests")
    parser.add_argument('request_id', help='Request ID to trace')
    parser.add_argument('--compare', help='Compare with another request ID')
    parser.add_argument('--export', help='Export trace to file')
    parser.add_argument('--trace-dir', help='Path to trace directory')

    args = parser.parse_args()

    tracer = RequestTracer(args.trace_dir)

    if args.compare:
        comparison = tracer.compare_requests(args.request_id, args.compare)
        print(json.dumps(comparison, indent=2, default=str))
    else:
        if args.export:
            trace = tracer.trace_recommendation_flow(args.request_id)
            with open(args.export, 'w', encoding='utf-8') as f:
                json.dump(trace, f, indent=2, default=str)
            print(f"Trace exported to {args.export}")
        else:
            tracer.print_recommendation_flow(args.request_id)


if __name__ == '__main__':
    main()
