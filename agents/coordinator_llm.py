"""
LLM Coordinator agent for orchestrated business analytics pipeline.
Controls workflow, context management, and agent interaction sequence.
"""

from agents.agent_roles_llm import AGENT_ROLES
from core.context import SharedContext

class LLMCoordinatorAgent:
    def __init__(self):
        self.agents = AGENT_ROLES
        self.context = SharedContext()

    async def execute_pipeline(self, csv_path):
        # 1. Load data and validate
        loader = self.agents["DataLoader"]
        data_load_result = await loader.act(
            user_input="Load and validate business data from the provided CSV file.",
            context={"csv_path": csv_path}
        )
        self.context.set("data_load_result", data_load_result)

        # 2. Analyze business metrics
        analyst = self.agents["Analyst"]
        analysis_result = await analyst.act(
            user_input="Analyze the loaded dataset for anomalies, patterns, and root causes.",
            context={"dataset": data_load_result}
        )
        self.context.set("analysis_result", analysis_result)

        # 3. Generate recommendations
        recommender = self.agents["Recommender"]
        recommendation_result = await recommender.act(
            user_input="Generate actionable business recommendations based on the analysis.",
            context={"analysis": analysis_result}
        )
        self.context.set("recommendation_result", recommendation_result)

        # 4. Critique results
        critic = self.agents["Critic"]
        critique_result = await critic.act(
            user_input="Review the previous outputs for errors, gaps, and logical consistency.",
            context={
                "data_load_result": data_load_result,
                "analysis_result": analysis_result,
                "recommendation_result": recommendation_result
            }
        )
        self.context.set("critique_result", critique_result)

        # 5. Summary and export (Coordinator)
        coordinator = self.agents["Coordinator"]
        final_summary = await coordinator.act(
            user_input="Summarize the results, agent outputs and critique. Generate a final report.",
            context={
                "data_load_result": data_load_result,
                "analysis_result": analysis_result,
                "recommendation_result": recommendation_result,
                "critique_result": critique_result
            }
        )
        self.context.set("final_summary", final_summary)
        return final_summary
