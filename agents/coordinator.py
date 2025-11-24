# agents/coordinator.py
"""
Coordinator Agent - Multi-Agent Orchestration

Orchestrates data loading, analysis, and recommendation generation
through specialized sub-agents with shared context.
"""

import asyncio
from tools import (
    ToolRegistry, 
    DataLoaderTool, 
    AnomalyDetectorTool, 
    MarketTrendsTool, 
    ReportGeneratorTool, 
    ActionLoggerTool
)
from core.context import SharedContext
from agents.analyst import AnalystAgent
from agents.recommendation import RecommendationAgent


class CoordinatorAgent:
    """Main coordinator with multi-agent orchestration."""
    
    def __init__(self):
        # Tool registry setup
        self.registry = ToolRegistry()
        self.registry.register(DataLoaderTool())
        self.registry.register(AnomalyDetectorTool())
        self.registry.register(MarketTrendsTool())
        self.registry.register(ReportGeneratorTool())
        self.registry.register(ActionLoggerTool())
        
        # Shared context for agent communication
        self.context = SharedContext()
        
        # Sub-agents initialization
        self.analyst = AnalystAgent(self.registry, self.context)
        self.recommender = RecommendationAgent(self.registry, self.context)
        
        # Logger
        self.logger = self.registry.get_tool("log_agent_action")

    async def execute_analysis(self, filepath):
        """
        Execute full multi-agent analysis pipeline.
        
        Pipeline:
        1. Load and validate data
        2. Detect anomalies (IQR + Z-score)
        3. Deep analysis via AnalystAgent
        4. Generate recommendations via RecommendationAgent
        5. Create comprehensive HTML report
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Result object with report data
        """
        await self.logger.execute(
            agent_name="Coordinator",
            action="start_analysis",
            details={"file": filepath},
            level="INFO"
        )

        # Step 1: Load data
        loader = self.registry.get_tool("load_csv_data")
        load_result = await loader.execute(filepath=filepath, validate=True)
        
        if not load_result.success:
            await self.logger.execute(
                agent_name="Coordinator",
                action="error",
                details={"error": load_result.error},
                level="ERROR"
            )
            return None

        raw_data = load_result.data
        await self.context.set("raw_data", raw_data)

        # Step 2: Detect anomalies using multiple methods
        detector = self.registry.get_tool("detect_anomalies")
        revenue_values = [float(row['revenue']) for row in raw_data]
        
        # IQR method
        iqr_result = await detector.execute(
            data=revenue_values, 
            method="iqr", 
            threshold=1.5
        )
        
        # Z-score method
        zscore_result = await detector.execute(
            data=revenue_values, 
            method="zscore", 
            threshold=2.0
        )
        
        # Combine anomalies from both methods
        all_anomalies = set()
        if iqr_result.success:
            all_anomalies.update(iqr_result.data.get('anomalies', []))
        if zscore_result.success:
            all_anomalies.update(zscore_result.data.get('anomalies', []))
        
        anomalies = list(all_anomalies)
        
        if not anomalies:
            await self.logger.execute(
                agent_name="Coordinator",
                action="no_anomalies_found",
                details={"message": "No anomalies detected"},
                level="INFO"
            )
            # Still generate a report even without anomalies
            anomalies = []
        
        await self.context.set("detected_anomalies", anomalies)

        # Step 3: Deep analysis via AnalystAgent
        analysis_result = await self.analyst.analyze(raw_data, anomalies)
        analysis_dict = await self.context.get("analysis_result")

        # Step 4: Generate recommendations via RecommendationAgent
        recommendation_result = await self.recommender.generate_recommendations(analysis_dict)
        recommendation_dict = await self.context.get("recommendation_result")

        # Step 5: Prepare report data
        issues = []
        recommendations = []
        
        # Add issues from analysis
        for pattern in analysis_dict.get("patterns", []):
            for value in pattern.get("values", []):
                issues.append({
                    "description": f"{pattern['pattern_type'].capitalize()} detected in {pattern['metric']}: {value} ({pattern['magnitude']:.1f}% deviation)",
                    "severity": pattern['severity'].lower()
                })
        
        # Add recommendations from RecommendationAgent
        for action in recommendation_dict.get("action_items", [])[:5]:  # Top 5
            rec_text = f"[Priority {action['priority']}] {action['title']}: {action['description']}"
            recommendations.append(rec_text)

        report_data = {
            "title": "Business Analytics Report - Multi-Agent Analysis",
            "issues": issues if issues else [{"description": "No significant anomalies detected", "severity": "low"}],
            "recommendations": recommendations if recommendations else ["Continue monitoring business metrics"]
        }

        # Step 6: Generate HTML report
        generator = self.registry.get_tool("generate_report_html")
        report_result = await generator.execute(
            report_data=report_data,
            output_file="output/report.html"
        )

        await self.logger.execute(
            agent_name="Coordinator",
            action="analysis_complete",
            details={
                "anomalies_found": len(anomalies),
                "patterns_detected": len(analysis_dict.get("patterns", [])),
                "recommendations_generated": len(recommendations),
                "report_generated": report_result.success
            },
            level="INFO"
        )

        if report_result and getattr(report_result, "success", False):
            return report_result
        else:
            return None
