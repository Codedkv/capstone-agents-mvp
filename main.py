import asyncio
from agents.coordinator import CoordinatorAgent

async def main():
    coordinator = CoordinatorAgent()
    metrics_file = "data/sample_business_metrics.csv"

    try:
        result = await coordinator.execute_analysis(metrics_file)
        print("=== EXECUTION RESULT ===")
        print("Result object:", result)
        if result is None:
            print("Result is None - analysis failed or incomplete.")
        else:
            print("Result success:", getattr(result, "success", None))
            print("Result data:", getattr(result, "data", None))
        print("========================")
    except Exception as e:
        print(f"Exception during analysis: {e}")

if __name__ == "__main__":
    asyncio.run(main())
