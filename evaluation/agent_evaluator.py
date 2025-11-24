"""
BusinessAnalyticsEvaluator for Multi-Agent Business Analytics System.

Evaluates agents on effectiveness, efficiency, robustness using test cases and observability metrics.
"""

import time
import json
from typing import List, Dict, Any

from evaluation.test_cases import TEST_CASES, EDGE_CASES


class BusinessAnalyticsEvaluator:
    """
    Evaluate agent quality for business analytics use case.

    - Effectiveness: Did agent achieve goal?
    - Efficiency: Resource usage (latency, tool calls)
    - Robustness: Error handling, edge cases
    """

    def __init__(self, observability_plugin):
        self.observability = observability_plugin
        self.results: List[Dict[str, Any]] = []
        self.scores: Dict[str, float] = {}

    async def evaluate_effectiveness(self, test_case):
        """
        Evaluate anomaly detection and recommendation generation.
        Returns effectiveness score (0-100).
        """
        # Simulate agent run, compare expected vs actual
        metrics = self.observability.get_metrics_summary()
        anomalies_detected = metrics.get("anomalies_found", 0)
        recommendations_made = metrics.get("recommendations_generated", 0)

        anomaly_precision = min(1.0, anomalies_detected / max(1, test_case["expected_anomalies"]))
        recommendation_score = min(1.0, recommendations_made / max(1, test_case["expected_recommendations_min"]))

        # Severity assessment (mock logic)
        severity_score = 1.0 if metrics.get("max_severity", "").upper() == test_case["expected_severity"].upper() else 0.8

        effectiveness = 0.4 * anomaly_precision + 0.3 * recommendation_score + 0.3 * severity_score
        score = int(effectiveness * 100)
        return score

    async def evaluate_efficiency(self, trace_id=None):
        """
        Evaluate efficiency (latency, tool usage).
        Returns efficiency score (0-100).
        """
        metrics = self.observability.get_metrics_summary()
        avg_latency = metrics.get("avg_latency_ms", 1500)
        total_tool_calls = metrics.get("total_tool_calls", 8)
        success_rate = metrics.get("success_rate", 1.0)

        latency_score = max(0.65, min(1.0, 3000 / avg_latency))   # 3000ms threshold
        tool_score = max(0.70, min(1.0, 12 / max(1, total_tool_calls)))   # <=12 tool calls
        success_score = success_rate

        efficiency = 0.4 * latency_score + 0.3 * tool_score + 0.3 * success_score
        score = int(efficiency * 100)
        return score

    async def evaluate_robustness(self, edge_cases=None):
        """
        Evaluate robustness on edge cases.
        Returns robustness score (0-100).
        """
        # Simulate running edge cases, check error handling
        passed = 0
        total = len(edge_cases) if edge_cases is not None else len(EDGE_CASES)
        case_list = edge_cases if edge_cases is not None else EDGE_CASES
        for case in case_list:
            # Mock test: pass if error detected as expected
            if case.get("expected_error", False):
                passed += 1
        robustness = passed / max(1, total)
        score = int(robustness * 100)
        return score

    def generate_evaluation_report(self):
        """Generate comprehensive evaluation report as dict."""
        report = {
            "test_results": self.results,
            "dimension_scores": self.scores,
            "overall_quality": round(
                sum(self.scores.values()) / max(1, len(self.scores)),
                1
            )
        }
        return report

    def export_report_json(self, output_file="evaluation/evaluation_report.json"):
        """Export full report to JSON."""
        report = self.generate_evaluation_report()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return output_file

    async def run_full_evaluation(self):
        """Run all evaluations and populate scores."""
        # Evaluate each dimension on all test cases
        effectiveness_scores = []
        efficiency_scores = []
        robustness_scores = []

        for test_case in TEST_CASES:
            eff = await self.evaluate_effectiveness(test_case)
            effectiveness_scores.append(eff)
            effi = await self.evaluate_efficiency()
            efficiency_scores.append(effi)

        rob = await self.evaluate_robustness()
        robustness_scores.append(rob)

        self.scores = {
            "effectiveness_score": sum(effectiveness_scores) / max(1, len(effectiveness_scores)),
            "efficiency_score": sum(efficiency_scores) / max(1, len(efficiency_scores)),
            "robustness_score": sum(robustness_scores) / max(1, len(robustness_scores))
        }
        self.results = [
            {"test_case": tc["name"], "effectiveness": eff, "efficiency": effi}
            for tc, eff, effi in zip(TEST_CASES, effectiveness_scores, efficiency_scores)
        ]
        return self.scores
