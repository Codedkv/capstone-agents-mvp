"""
LLM Agent initialization for production business analytics system.
Defines and exports all main agent classes for orchestrated multi-agent workflow.
"""

from core.agent_base_llm import LLMAgent
from config.agent_prompts import AGENT_PROMPTS
from tools.data_loader import load_csv_data, validate_schema
from tools.anomaly_detector import detect_anomalies
from tools.market_trends import search_trends
from tools.report_generator import generate_report_html
from tools.action_logger import log_agent_action

# Specify agent-tool assignments (use only what agents actually need):
DATA_LOADER_TOOLS = [load_csv_data, validate_schema]
ANALYST_TOOLS = [detect_anomalies, search_trends, log_agent_action]
RECOMMENDER_TOOLS = [generate_report_html, search_trends, log_agent_action]
COORDINATOR_TOOLS = []  # For now, Coordinator manages logic, not direct tools
CRITIC_TOOLS = []       # Critic reviews output, does not call tools

# Production agent instances
CoordinatorAgent = LLMAgent(
    role_name="Coordinator",
    system_instruction=AGENT_PROMPTS["Coordinator"],
    toolset=COORDINATOR_TOOLS
)
DataLoaderAgent = LLMAgent(
    role_name="DataLoader",
    system_instruction=AGENT_PROMPTS["DataLoader"],
    toolset=DATA_LOADER_TOOLS
)
AnalystAgent = LLMAgent(
    role_name="Analyst",
    system_instruction=AGENT_PROMPTS["Analyst"],
    toolset=ANALYST_TOOLS
)
RecommenderAgent = LLMAgent(
    role_name="Recommender",
    system_instruction=AGENT_PROMPTS["Recommender"],
    toolset=RECOMMENDER_TOOLS
)
CriticAgent = LLMAgent(
    role_name="Critic",
    system_instruction=AGENT_PROMPTS["Critic"],
    toolset=CRITIC_TOOLS
)

# Export ready-to-use objects for orchestrator
AGENT_ROLES = {
    "Coordinator": CoordinatorAgent,
    "DataLoader": DataLoaderAgent,
    "Analyst": AnalystAgent,
    "Recommender": RecommenderAgent,
    "Critic": CriticAgent
}
