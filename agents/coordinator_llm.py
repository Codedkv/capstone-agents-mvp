from agents.agent_roles_llm import AGENT_ROLES
from core.agent_base_llm import LLMAgent
from tools.report_generator import generate_report_html
import json
import os

class LLMCoordinatorAgent:
    def __init__(self):
        self.agents = AGENT_ROLES
        self.context = {}

    async def execute_pipeline(self, metrics_file):
        """
        Execute the full multi-agent pipeline sequentially.
        """
        print("\n=== STARTING CAPSTONE AGENT PIPELINE ===\n")
        
        # 1. Load Data (DataLoader)
        loader = self.agents["DataLoader"]
        data_load_result = await loader.act(
            user_input="Load and validate the file 'data/shipments_data.xlsx'. Return the filepath.",
        )
        # FIX: Removed 'await', standard dict update
        self.context.update({"data_load_result": data_load_result})

        # Extract filepath safely
        filepath = "data/shipments_data.xlsx" 
        if isinstance(data_load_result, dict) and "filename" in data_load_result:
             filepath = os.path.join("data", data_load_result["filename"])

        # 2. Analyze Data (Analyst) - Pass FILEPATH
        analyst = self.agents["Analyst"]
        analysis_result = await analyst.act(
            user_input=f"The data is located at '{filepath}'. Use your tools to detect anomalies and search trends in this file.",
            context={"filepath": filepath}
        )
        # FIX: Removed 'await'
        self.context.update({"analysis_result": analysis_result})

        # 3. Recommendations (Recommender)
        recommender = self.agents["Recommender"]
        recommendation_result = await recommender.act(
            user_input=f"Based on the analysis below, provide business recommendations. Filepath is '{filepath}'.",
            context={"analysis_result": analysis_result, "filepath": filepath}
        )
        # FIX: Removed 'await'
        self.context.update({"recommendation_result": recommendation_result})

        # 4. Critique (Critic)
        critic = self.agents["Critic"]
        critique_result = await critic.act(
            user_input="Review the previous steps. Check if the analysis used the tools correctly and if recommendations match the findings.",
            context={
                "data_load_result": data_load_result,
                "analysis_result": analysis_result,
                "recommendation_result": recommendation_result
            }
        )
        # FIX: Removed 'await'
        self.context.update({"critique_result": critique_result})

        # 5. Summary (Coordinator)
        coordinator = self.agents["Coordinator"]
        final_summary = await coordinator.act(
            user_input="Synthesize all findings into a final executive summary text.",
            context={
                "analysis_result": analysis_result,
                "recommendation_result": recommendation_result,
                "critique_result": critique_result
            }
        )
        
        # 6. FORCE REPORT GENERATION
        print("\n[System] Auto-generating HTML report...")
        report_status = generate_report_html(
            analysis_result=analysis_result,
            recommendation_result=recommendation_result,
            critique_result=critique_result,
            summary=final_summary,
            output_path="output/analysis_report.html"
        )
        print(f"[System] Report generation status: {report_status}")

        # FIX: Removed 'await'
        self.context.update({"final_summary": final_summary})
        return final_summary
