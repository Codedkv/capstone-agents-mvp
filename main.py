import asyncio
import os
import sys
from dotenv import load_dotenv
from agents.coordinator import CoordinatorAgent
from evaluation.agent_evaluator import BusinessAnalyticsEvaluator
from evaluation.test_cases import get_all_test_case_names

# Load environment variables
load_dotenv()


async def analyze(metrics_file):
    coordinator = CoordinatorAgent()
    result = await coordinator.execute_analysis(metrics_file)

    print("=== EXECUTION RESULT ===")
    if result is None:
        print("Result is None - analysis failed or incomplete.")
    else:
        print("Success:", getattr(result, "success", None))
        if hasattr(result, "data") and result.data:
            print("\nReport generated successfully!")
            if result.data.get("file_saved"):
                print(f"Report saved to: {result.data.get('file_path')}")
    print("========================")

    # Print observability metrics
    print("\n=== OBSERVABILITY METRICS ===")
    metrics = coordinator.observability.get_metrics_summary()
    for k, v in metrics.items():
        print(f"{k}: {v}")

    # Return coordinator for other modes
    return coordinator

async def show_metrics(metrics_file):
    coordinator = CoordinatorAgent()
    await coordinator.execute_analysis(metrics_file)
    print("\n=== OBSERVABILITY METRICS ===")
    metrics = coordinator.observability.get_metrics_summary()
    for k, v in metrics.items():
        print(f"{k}: {v}")
    coordinator.observability.export_metrics_json("output/metrics.json")

async def export_traces(metrics_file):
    coordinator = CoordinatorAgent()
    await coordinator.execute_analysis(metrics_file)
    coordinator.observability.export_traces_json("output/traces.json")
    print("\nTraces exported to output/traces.json")
    coordinator.observability.export_metrics_json("output/metrics.json")
    print("Metrics exported to output/metrics.json")

async def evaluate(metrics_file):
    coordinator = CoordinatorAgent()
    await coordinator.execute_analysis(metrics_file)
    evaluator = BusinessAnalyticsEvaluator(coordinator.observability)
    await evaluator.run_full_evaluation()
    report = evaluator.generate_evaluation_report()
    evaluator.export_report_json("output/evaluation_report.json")

    print("\n=== EVALUATION SCORE ===")
    print(f"Overall Quality: {report['overall_quality']:.2f}/100")
    for dim, score in report["dimension_scores"].items():
        print(f"{dim}: {score:.2f}")
    print("\nTest Results:")
    for r in report["test_results"]:
        print(f"- {r['test_case']}: effectiveness={r['effectiveness']}, efficiency={r['efficiency']}")
    print("Report exported to output/evaluation_report.json")


if __name__ == "__main__":
    # CLI usage: python main.py [mode] [filename]
    if len(sys.argv) < 2:
        print("Usage: python main.py [analyze|metrics|export-traces|evaluate] [filename]")
        sys.exit(1)
    mode = sys.argv[1]
    metrics_file = sys.argv[2] if len(sys.argv) > 2 else "data/sample_business_metrics.csv"

    if mode == "analyze":
        asyncio.run(analyze(metrics_file))
    elif mode == "metrics":
        asyncio.run(show_metrics(metrics_file))
    elif mode == "export-traces":
        asyncio.run(export_traces(metrics_file))
    elif mode == "evaluate":
        asyncio.run(evaluate(metrics_file))
    else:
        print(f"Unknown mode: {mode}")
        print("Supported modes: analyze, metrics, export-traces, evaluate")
        sys.exit(1)
