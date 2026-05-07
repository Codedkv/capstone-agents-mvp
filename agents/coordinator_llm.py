import os
from agents.agent_roles_llm import init_agents
from tools.report_generator import generate_report_html


class LLMCoordinatorAgent:
    """
    Sequentially executes the 5-agent LLM pipeline:
    DataLoader -> Analyst -> Recommender -> Critic -> Coordinator (summary).

    Parameters
    ----------
    api_key : str | None
        Gemini API key. If None, falls back on env vars (GOOGLE_API_KEY /
        GEMINI_API_KEY) inside GeminiClient. Pass an explicit key from the
        backend layer for BYOK (bring-your-own-key) flows.
    event_emitter : object | None
        Optional emitter exposing `async emit(event_type: str, data: dict)`.
        See backend/events.py for the contract. When None the pipeline runs
        silently (preserves the original CLI behaviour).
    """

    EVENT_TYPES = (
        "pipeline.start",
        "agent.start",
        "agent.end",
        "pipeline.end",
        "error",
    )

    def __init__(self, api_key=None, event_emitter=None):
        self.api_key = api_key
        self.event_emitter = event_emitter
        self.agents = init_agents(api_key)
        self.context = {}

    async def _emit(self, event_type, data):
        if self.event_emitter is not None:
            await self.event_emitter.emit(event_type, data)

    @staticmethod
    def _summarise(value, limit=200):
        text = value if isinstance(value, str) else str(value)
        return text if len(text) <= limit else text[:limit] + "..."

    async def execute_pipeline(self, metrics_file, output_path="output/analysis_report.html"):
        """
        Run the full 5-agent pipeline against `metrics_file` and write the
        final HTML report to `output_path`. Returns the executive summary
        string produced by the Coordinator agent.
        """
        await self._emit("pipeline.start", {"file": metrics_file, "output_path": output_path})

        try:
            # 1. DataLoader
            await self._emit("agent.start", {"agent": "DataLoader"})
            loader = self.agents["DataLoader"]
            data_load_result = await loader.act(
                user_input=(
                    f"Load and validate the file '{metrics_file}'. "
                    "Return the filepath and a short summary."
                ),
            )
            self.context["data_load_result"] = data_load_result
            await self._emit("agent.end", {
                "agent": "DataLoader",
                "summary": self._summarise(data_load_result),
            })

            # The metrics_file argument is authoritative — DataLoader's tool
            # call is for validation and side effects, not for selecting the
            # file. If the agent reports a different filename that exists on
            # disk inside the same directory, we trust it.
            filepath = metrics_file
            if isinstance(data_load_result, dict) and "filename" in data_load_result:
                directory = os.path.dirname(metrics_file) or "data"
                candidate = os.path.join(directory, data_load_result["filename"])
                if os.path.exists(candidate):
                    filepath = candidate

            # 2. Analyst
            await self._emit("agent.start", {"agent": "Analyst"})
            analyst = self.agents["Analyst"]
            analysis_result = await analyst.act(
                user_input=(
                    f"The data is located at '{filepath}'. "
                    "Use your tools to detect anomalies and search trends in this file."
                ),
                context={"filepath": filepath},
            )
            self.context["analysis_result"] = analysis_result
            await self._emit("agent.end", {
                "agent": "Analyst",
                "summary": self._summarise(analysis_result),
            })

            # 3. Recommender
            await self._emit("agent.start", {"agent": "Recommender"})
            recommender = self.agents["Recommender"]
            recommendation_result = await recommender.act(
                user_input=(
                    "Based on the analysis below, provide business recommendations. "
                    f"Filepath is '{filepath}'."
                ),
                context={"analysis_result": analysis_result, "filepath": filepath},
            )
            self.context["recommendation_result"] = recommendation_result
            await self._emit("agent.end", {
                "agent": "Recommender",
                "summary": self._summarise(recommendation_result),
            })

            # 4. Critic
            await self._emit("agent.start", {"agent": "Critic"})
            critic = self.agents["Critic"]
            critique_result = await critic.act(
                user_input=(
                    "Review the previous steps. Check if the analysis used the tools "
                    "correctly and if recommendations match the findings."
                ),
                context={
                    "data_load_result": data_load_result,
                    "analysis_result": analysis_result,
                    "recommendation_result": recommendation_result,
                },
            )
            self.context["critique_result"] = critique_result
            await self._emit("agent.end", {
                "agent": "Critic",
                "summary": self._summarise(critique_result),
            })

            # 5. Coordinator (summary)
            await self._emit("agent.start", {"agent": "Coordinator"})
            coordinator = self.agents["Coordinator"]
            final_summary = await coordinator.act(
                user_input="Synthesize all findings into a final executive summary text.",
                context={
                    "analysis_result": analysis_result,
                    "recommendation_result": recommendation_result,
                    "critique_result": critique_result,
                },
            )
            self.context["final_summary"] = final_summary
            await self._emit("agent.end", {
                "agent": "Coordinator",
                "summary": self._summarise(final_summary),
            })

            # 6. Forced HTML report (double-safety: even if the Coordinator
            # agent did not call generate_report_html itself).
            report_status = generate_report_html(
                analysis_result=analysis_result,
                recommendation_result=recommendation_result,
                critique_result=critique_result,
                summary=final_summary,
                output_path=output_path,
            )

            await self._emit("pipeline.end", {
                "output_path": output_path,
                "report_status": report_status.get("status") if isinstance(report_status, dict) else "unknown",
            })

            return final_summary

        except Exception as exc:
            await self._emit("error", {"message": str(exc)})
            raise
