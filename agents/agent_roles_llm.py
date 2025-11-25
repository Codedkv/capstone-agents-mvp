"""
LLM Agent initialization for production business analytics system.
Defines and exports all main agent classes for orchestrated multi-agent workflow.
"""

from core.agent_base_llm import LLMAgent
from config.agent_prompts import AGENT_PROMPTS

from tools.data_loader import load_data
from tools.anomaly_detector import detect_anomalies
from tools.market_trends import search_trends
from tools.report_generator import generate_report_html
from tools.action_logger import log_agent_action

DEFAULT_CONFIG_PATH = "config/analysis_settings.json"

def load_data_with_config(filepath, config_path=DEFAULT_CONFIG_PATH):
    return load_data(filepath=filepath, config_path=config_path)

def detect_anomalies_with_config(data, config_path=DEFAULT_CONFIG_PATH):
    return detect_anomalies(data=data, config_path=config_path)

def search_trends_with_config(*args, config_path=DEFAULT_CONFIG_PATH, **kwargs):
    return search_trends(*args, config_path=config_path, **kwargs)

DATA_LOADER_TOOLS = [load_data_with_config]
ANALYST_TOOLS = [detect_anomalies_with_config, search_trends_with_config, log_agent_action]
RECOMMENDER_TOOLS = [generate_report_html, search_trends_with_config, log_agent_action]
COORDINATOR_TOOLS = []
CRITIC_TOOLS = []

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

AGENT_ROLES = {
    "Coordinator": CoordinatorAgent,
    "DataLoader": DataLoaderAgent,
    "Analyst": AnalystAgent,
    "Recommender": RecommenderAgent,
    "Critic": CriticAgent
}
