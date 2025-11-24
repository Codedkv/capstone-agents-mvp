import asyncio
import os
from dotenv import load_dotenv
from agents.coordinator import CoordinatorAgent

# Load environment variables
load_dotenv()

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
            if hasattr(result, "data") and result.data:
                print("\nReport generated successfully!")
                if result.data.get("file_saved"):
                    print(f"Report saved to: {result.data.get('file_path')}")
        print("========================")
        
    except Exception as e:
        print(f"Exception during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
