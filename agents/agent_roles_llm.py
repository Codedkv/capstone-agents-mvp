from tools.data_loader import load_data
from tools.anomaly_detector import detect_anomalies
from tools.market_trends import search_trends
from tools.report_generator import generate_report_html
from tools.action_logger import log_agent_action
from config.agent_prompts import AGENT_PROMPTS
from core.agent_base_llm import LLMAgent

# Toolsets per agent role
DATA_LOADER_TOOLS = [load_data, log_agent_action]
ANALYST_TOOLS = [detect_anomalies, search_trends, log_agent_action]
RECOMMENDER_TOOLS = [search_trends, log_agent_action]
COORDINATOR_TOOLS = [generate_report_html, log_agent_action]
CRITIC_TOOLS = [log_agent_action]


def init_agents(api_key=None):
    """
    Build a fresh set of LLM agents bound to the given Gemini api_key.

    Pass api_key=None to fall back on env vars (GOOGLE_API_KEY / GEMINI_API_KEY).
    Always called per-run rather than at import time so a multi-tenant backend
    can switch keys between runs (BYOK).
    """
    return {
        "DataLoader": LLMAgent(
            role_name="DataLoader",
            system_instruction=AGENT_PROMPTS["DataLoader"],
            toolset=DATA_LOADER_TOOLS,
            api_key=api_key,
        ),
        "Analyst": LLMAgent(
            role_name="Analyst",
            system_instruction=AGENT_PROMPTS["Analyst"],
            toolset=ANALYST_TOOLS,
            api_key=api_key,
        ),
        "Recommender": LLMAgent(
            role_name="Recommender",
            system_instruction=AGENT_PROMPTS["Recommender"],
            toolset=RECOMMENDER_TOOLS,
            api_key=api_key,
        ),
        "Critic": LLMAgent(
            role_name="Critic",
            system_instruction=AGENT_PROMPTS["Critic"],
            toolset=CRITIC_TOOLS,
            api_key=api_key,
        ),
        "Coordinator": LLMAgent(
            role_name="Coordinator",
            system_instruction=AGENT_PROMPTS["Coordinator"],
            toolset=COORDINATOR_TOOLS,
            api_key=api_key,
        ),
    }
