"""
ADK-compatible tool functions for Kaggle Agent Development Kit integration.

These wrappers convert existing tool classes to simple Python functions
that work with ADK's function calling system.
"""

import asyncio
from typing import Dict, List, Any, Optional
from tools import (
    DataLoaderTool,
    AnomalyDetectorTool,
    MarketTrendsTool,
    ReportGeneratorTool,
    ActionLoggerTool
)


# Initialize tool instances (singleton pattern)
_data_loader = DataLoaderTool()
_anomaly_detector = AnomalyDetectorTool()
_market_trends = MarketTrendsTool()
_report_generator = ReportGeneratorTool()
_action_logger = ActionLoggerTool()


def load_csv_data(
    filepath: str,
    validate: bool = True,
    max_rows: int = 10000
) -> Dict[str, Any]:
    """
    Load and validate CSV files with business metrics.
    
    Args:
        filepath: Path to CSV file
        validate: Validate data schema and types
        max_rows: Maximum rows to load
        
    Returns:
        Dictionary with data, row_count, and columns
    """
    result = asyncio.run(_data_loader.execute(
        filepath=filepath,
        validate=validate,
        max_rows=max_rows
    ))
    
    if result.success:
        return {
            "status": "success",
            "data": result.data,
            "row_count": len(result.data) if isinstance(result.data, list) else 0
        }
    else:
        return {
            "status": "error",
            "error": result.error
        }


def detect_anomalies(
    data: List[float],
    method: str = "iqr",
    threshold: float = 1.5
) -> Dict[str, Any]:
    """
    Detect anomalies in numerical data using statistical methods.
    
    Args:
        data: List of numerical values
        method: Detection method (iqr, zscore, threshold)
        threshold: Threshold for anomaly detection
        
    Returns:
        Dictionary with anomalies, count, and method used
    """
    result = asyncio.run(_anomaly_detector.execute(
        data=data,
        method=method,
        threshold=threshold
    ))
    
    if result.success:
        return {
            "status": "success",
            "anomalies": result.data.get("anomalies", []),
            "count": result.data.get("count", 0),
            "method": result.data.get("method", method)
        }
    else:
        return {
            "status": "error",
            "error": result.error
        }


def search_market_trends(
    topic: str,
    region: str = "Global",
    use_api: bool = True,
    max_results: int = 5
) -> Dict[str, Any]:
    """
    Search for market trends using Google API or mock data.
    
    Args:
        topic: Search topic/query
        region: Geographic region for search
        use_api: Whether to use real API (True) or mock (False)
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with trends, region, and source
    """
    result = asyncio.run(_market_trends.execute(
        topic=topic,
        region=region,
        use_api=use_api,
        max_results=max_results
    ))
    
    if result.success:
        return {
            "status": "success",
            "trends": result.data.get("trends", []),
            "region": result.data.get("region", region),
            "source": result.data.get("source", "Unknown")
        }
    else:
        return {
            "status": "error",
            "error": result.error
        }


def generate_report_html(
    report_data: Dict[str, Any],
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate HTML report from analysis results.
    
    Args:
        report_data: Dictionary with title, issues, and recommendations
        output_file: Optional path to save HTML file
        
    Returns:
        Dictionary with html content, file_saved status, and file_path
    """
    result = asyncio.run(_report_generator.execute(
        report_data=report_data,
        output_file=output_file
    ))
    
    if result.success:
        return {
            "status": "success",
            "html": result.data.get("html", ""),
            "file_saved": result.data.get("file_saved", False),
            "file_path": result.data.get("file_path")
        }
    else:
        return {
            "status": "error",
            "error": result.error
        }


def log_agent_action(
    agent_name: str,
    action: str,
    details: Optional[Dict[str, Any]] = None,
    level: str = "INFO"
) -> Dict[str, Any]:
    """
    Log agent actions to JSONL file.
    
    Args:
        agent_name: Name of the agent performing the action
        action: Action description
        details: Additional details dictionary
        level: Log level (INFO, WARNING, ERROR)
        
    Returns:
        Dictionary with logged status, log_file, and entry
    """
    result = asyncio.run(_action_logger.execute(
        agent_name=agent_name,
        action=action,
        details=details or {},
        level=level
    ))
    
    if result.success:
        return {
            "status": "success",
            "logged": result.data.get("logged", False),
            "log_file": result.data.get("log_file"),
            "entry": result.data.get("entry")
        }
    else:
        return {
            "status": "error",
            "error": result.error
        }


# Export all ADK-compatible tools
__all__ = [
    'load_csv_data',
    'detect_anomalies',
    'search_market_trends',
    'generate_report_html',
    'log_agent_action'
]
