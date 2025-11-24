from tools import ToolRegistry, DataLoaderTool, AnomalyDetectorTool, MarketTrendsTool, ReportGeneratorTool, ActionLoggerTool

class CoordinatorAgent:
    """Main coordinator with tool support."""
    
    def __init__(self):
        self.registry = ToolRegistry()
        self.registry.register(DataLoaderTool())
        self.registry.register(AnomalyDetectorTool())
        self.registry.register(MarketTrendsTool())
        self.registry.register(ReportGeneratorTool())
        self.registry.register(ActionLoggerTool())
        self.logger = self.registry.get_tool("log_agent_action")

    async def execute_analysis(self, filepath):
        await self.logger.execute(
            agent_name="Coordinator",
            action="start_analysis",
            details={"file": filepath},
            level="INFO"
        )

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

        detector = self.registry.get_tool("detect_anomalies")
        revenue_values = [float(row['revenue']) for row in load_result.data]
        anomaly_result = await detector.execute(data=revenue_values, method="iqr", threshold=1.5)
        
        if not anomaly_result.success:
            await self.logger.execute(
                agent_name="Coordinator",
                action="error",
                details={"error": anomaly_result.error},
                level="ERROR"
            )
            return None

        issues = []
        recommendations = []
        
        if anomaly_result.data.get('count', 0) > 0:
            for anomaly_value in anomaly_result.data.get('anomalies', []):
                issues.append({
                    "description": f"Anomaly detected: {anomaly_value}",
                    "severity": "high"
                })

        report_data = {
            "title": "Analysis Report",
            "issues": issues,
            "recommendations": recommendations
        }

        generator = self.registry.get_tool("generate_report_html")
        report_result = await generator.execute(
            report_data=report_data,
            output_file="output/report.html"
        )

        await self.logger.execute(
            agent_name="Coordinator",
            action="analysis_complete",
            details={
                "anomalies_found": anomaly_result.data.get('count', 0),
                "report_generated": report_result.success
            },
            level="INFO"
        )

        if report_result and getattr(report_result, "success", False):
            return report_result
        else:
            return None
