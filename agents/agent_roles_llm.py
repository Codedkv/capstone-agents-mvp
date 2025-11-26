from tools.data_loader import load_data
from tools.anomaly_detector import detect_anomalies
from tools.market_trends import search_trends
from tools.report_generator import generate_report_html
from tools.action_logger import log_agent_action
from config.agent_prompts import AGENT_PROMPTS
from core.agent_base_llm import LLMAgent

# Define toolsets for each agent
DATA_LOADER_TOOLS = [load_data, log_agent_action]
ANALYST_TOOLS = [detect_anomalies, search_trends, log_agent_action]
RECOMMENDER_TOOLS = [search_trends, log_agent_action]
# Coordinator needs generate_report_html to finalize the pipeline
COORDINATOR_TOOLS = [generate_report_html, log_agent_action]
CRITIC_TOOLS = [log_agent_action]

def init_agents():
    """
    Initialize and return a dictionary of LLM agents with their specific roles and tools.
    """
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

    CoordinatorAgent = LLMAgent(
        role_name="Coordinator",
        system_instruction=AGENT_PROMPTS["Coordinator"],
        toolset=COORDINATOR_TOOLS
    )

    return {
        "DataLoader": DataLoaderAgent,
        "Analyst": AnalystAgent,
        "Recommender": RecommenderAgent,
        "Critic": CriticAgent,
        "Coordinator": CoordinatorAgent
    }

# Initialize agents so other modules can import AGENT_ROLES
AGENT_ROLES = init_agents()
