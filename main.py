import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from agents.coordinator_llm import LLMCoordinatorAgent
from core.paths import DEFAULT_ENV_FILE, DEFAULT_METRICS_FILE, PROJECT_ROOT

load_dotenv(DEFAULT_ENV_FILE)

async def main():
    llm_coordinator = LLMCoordinatorAgent()
    raw = os.getenv("METRICS_FILE", str(DEFAULT_METRICS_FILE))
    metrics_path = Path(raw)
    if not metrics_path.is_absolute():
        metrics_path = (PROJECT_ROOT / metrics_path).resolve()
    metrics_file = str(metrics_path)
    final_result = await llm_coordinator.execute_pipeline(metrics_file)

    print("=== FINAL LLM PIPELINE RESULT ===")
    print(final_result)
    print("===============================")

if __name__ == "__main__":
    asyncio.run(main())
