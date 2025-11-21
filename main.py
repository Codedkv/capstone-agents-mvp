import asyncio
from agents.coordinator import CoordinatorAgent
from agents.mock_agents import (
    HistoricalAnalyzerAgent,
    LiveMonitorAgent,
    RecommenderAgent
)
from agents.base_agents import AgentConfig
from core.session_manager import SessionManager
from core.logging_system import StructuredLogger, MetricsCollector

# Инициализация компонентов
logger = StructuredLogger(verbose=True)
metrics = MetricsCollector()
session_manager = SessionManager(storage_dir="./sessions")

# Конфиг координатора
coord_config = AgentConfig(
    name="Coordinator",
    agent_type="coordinator"
)
coordinator = CoordinatorAgent(coord_config, session_manager, logger, metrics)

# Регистрация mock под-агентов
coordinator.register_sub_agent(
    "historical_analyzer",
    HistoricalAnalyzerAgent(AgentConfig(name="HistoricalAnalyzer", agent_type="analyzer"))
)
coordinator.register_sub_agent(
    "live_monitor",
    LiveMonitorAgent(AgentConfig(name="LiveMonitor", agent_type="monitor"))
)
coordinator.register_sub_agent(
    "recommender",
    RecommenderAgent(AgentConfig(name="Recommender", agent_type="recommender"))
)

# Основная функция запуска анализа
async def main():
    context = {
        "company_name": "Acme Corp",
        "analysis_period": "Q4 2024",
        "metrics_file": "data/sample_business_metrics.csv"
    }
    response = await coordinator.execute(
        "Analyze Q4 business performance and identify bottlenecks",
        context
    )
    print("Analysis Complete!")
    print(f"Status: {response.status}")
    print(f"Issues Found: {response.result.get('total_issues_found')}")
    print(f"Recommendations: {len(response.result.get('recommendations', []))}")
    print(f"Execution Time: {getattr(response, 'execution_time_ms', None)}ms")

if __name__ == "__main__":
    asyncio.run(main())
