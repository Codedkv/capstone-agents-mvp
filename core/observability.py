"""
ObservabilityPlugin for Multi-Agent Business Analytics System.

Implements ADK-style observability: traces, metrics, error tracking.
"""

import json
import os
import time
from typing import List, Dict, Any
from datetime import datetime

class ObservabilityPlugin:
    """
    ADK-style Observability Plugin.

    Responsibilities:
    - Log all agent and tool invocations
    - Trace multi-agent workflows with trace_id/spans
    - Collect performance metrics: latency, success rate, error count
    - Export data to JSON for analysis
    """
    def __init__(self, log_dir="./logs"):
        self.log_dir = log_dir
        self.traces: Dict[str, Dict] = {}
        self.metrics = {
            "agent_calls": {},
            "tool_calls": {},
            "errors": [],
            "latencies": [],
            "anomalies_found": 0,
            "recommendations_generated": 0,
            "max_severity": "LOW"
        }

    async def before_agent_callback(self, agent_name, context):
        """Start agent execution trace."""
        trace_id = context.get("trace_id", str(time.time()))
        if trace_id not in self.traces:
            self.traces[trace_id] = {
                "start": datetime.now().isoformat(),
                "spans": [],
                "agent": agent_name
            }
        self.metrics["agent_calls"][agent_name] = self.metrics["agent_calls"].get(agent_name, 0) + 1
        self.traces[trace_id]["spans"].append({
            "name": f"{agent_name}_start",
            "timestamp": datetime.now().isoformat()
        })

    async def after_agent_callback(self, agent_name, context, result):
        """End agent execution, update metrics and trace."""
        trace_id = context.get("trace_id", str(time.time()))
        self.traces.setdefault(trace_id, {"spans": []})
        self.traces[trace_id]["spans"].append({
            "name": f"{agent_name}_end",
            "timestamp": datetime.now().isoformat()
        })
        # Collect domain metrics (if present in result)
        if getattr(result, "data", None):
            data = result.data
            self.metrics["anomalies_found"] = data.get("anomalies_found", self.metrics.get("anomalies_found", 0))
            self.metrics["recommendations_generated"] = data.get("recommendations_generated", self.metrics.get("recommendations_generated", 0))
            self.metrics["max_severity"] = data.get("max_severity", self.metrics.get("max_severity", "LOW"))
        self.metrics["latencies"].append(time.time())

    async def before_tool_callback(self, tool_name, tool_input):
        """Log tool invocation."""
        self.metrics["tool_calls"][tool_name] = self.metrics["tool_calls"].get(tool_name, 0) + 1

    async def after_tool_callback(self, tool_name, tool_output):
        """Log tool execution result."""
        # Optionally add more metrics

    async def on_error_callback(self, error, context):
        """Track errors with context info."""
        self.metrics["errors"].append({
            "error": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def get_trace(self, trace_id):
        """Get execution trace by ID."""
        return self.traces.get(trace_id, {})

    def get_metrics_summary(self):
        """Aggregate metrics for current session."""
        total_agent_calls = sum(self.metrics["agent_calls"].values())
        total_tool_calls = sum(self.metrics["tool_calls"].values())
        error_count = len(self.metrics["errors"])
        latencies = self.metrics["latencies"]
        avg_latency_ms = int(sum(latencies) / max(1, len(latencies)) * 1000) if latencies else 1000
        success_rate = 1.0 - (error_count / max(1, total_agent_calls))
        return {
            "total_agent_calls": total_agent_calls,
            "total_tool_calls": total_tool_calls,
            "error_count": error_count,
            "avg_latency_ms": avg_latency_ms,
            "success_rate": success_rate,
            "anomalies_found": self.metrics["anomalies_found"],
            "recommendations_generated": self.metrics["recommendations_generated"],
            "max_severity": self.metrics["max_severity"]
        }

    def export_traces_json(self, output_file="output/traces.json"):
        """Export all traces to JSON."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, indent=2)
        return output_file

    def export_metrics_json(self, output_file="output/metrics.json"):
        """Export aggregated metrics as JSON."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        metrics = self.get_metrics_summary()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        return output_file
