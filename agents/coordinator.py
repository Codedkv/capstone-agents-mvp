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
        revenue = [float(row.get("revenue", 0)) for row in load_result.data]
        anomaly_result = await detector.execute(data=revenue, method="iqr")

        issues = []
        if anomaly_result.success and anomaly_result.data.get("anomalies"):
            for anomaly in anomaly_result.data["anomalies"]:
                issues.append({"description": f"Anomaly detected: {anomaly}", "severity": "high"})
        else:
            issues.append({"description": "No anomalies detected", "severity": "low"})

        reporter = self.registry.get_tool("generate_report_html")

        import os
        output_dir = os.path.dirname("output/report.html")
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        report_result = await reporter.execute(
            report_data={
                "title": "Analysis Report",
                "issues": issues,
                "recommendations": []
            },
            output_file="output/report.html"
        )

        # Диагностический вывод для проверки результата генерации отчёта
        print("=== DIAGNOSTIC OUTPUT START ===")
        print("Load result success:", load_result.success)
        print("Anomaly detection success:", anomaly_result.success)
        print("Anomalies data:", anomaly_result.data if anomaly_result.success else anomaly_result.error)
        print("Report generation success:", getattr(report_result, "success", None))
        print("Report generation data:", getattr(report_result, "data", None))
        print("Report generation error:", getattr(report_result, "error", None))
        print("=== DIAGNOSTIC OUTPUT END ===")

        await self.logger.execute(
            agent_name="Coordinator",
            action="analysis_complete",
            details={"status": "success"},
            level="INFO"
        )

        if report_result and getattr(report_result, "success", False):
            return report_result
        else:
            return None
