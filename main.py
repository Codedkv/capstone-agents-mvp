import asyncio
import os
from dotenv import load_dotenv
from agents.coordinator_llm import LLMCoordinatorAgent

load_dotenv()

async def main():
    llm_coordinator = LLMCoordinatorAgent()
    metrics_file = os.getenv("METRICS_FILE", "data/sample_business_metrics.csv")
    final_result = await llm_coordinator.execute_pipeline(metrics_file)

    print("=== FINAL LLM PIPELINE RESULT ===")
    print(final_result)
    print("===============================")

if __name__ == "__main__":
    asyncio.run(main())
