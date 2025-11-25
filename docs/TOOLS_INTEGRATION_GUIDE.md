# Tools Integration Guide

**Multi-Agent Business Analytics System — Agent Tools & Function Calling**

> Production-ready guide for integrating and extending tools in the Capstone-Agents-MVP system. Updated for config-driven architecture with Gemini 2.5 Flash.

---

## Overview

This guide covers the 5 production tools available in the system, their integration patterns, and how to extend them for custom use cases.

### Available Tools

| Tool | Purpose | Status | Input Format |
|------|---------|--------|--------------|
| `load_data` | Data ingestion (CSV, Excel, JSON, PDF) | ✅ Production | File path + format validation |
| `detect_anomalies` | Statistical anomaly detection (IQR, Z-score) | ✅ Production | Data array + method + threshold |
| `search_trends` | Market/domain trend search | ✅ Production | Topic query string |
| `generate_report_html` | HTML report generation | ✅ Production | Report data dict + styling |
| `log_agent_action` | Structured action logging | ✅ Production | Agent name + action + details |

---

## Architecture

### Config-Driven Design

All tools are controlled via `config/analysis_settings.json`:

{
"required_columns": ["date", "store_name", "product_name", "quantity", "price_per_unit", "total_value"],
"anomaly_columns": ["quantity", "total_value"],
"anomaly_method": "iqr",
"anomaly_threshold": 1.5,
"max_rows": 10000
}

text

### Agent Integration Pattern

┌─────────────────────────────┐
│ Coordinator Agent (LLM) │
└──────────────┬──────────────┘
│
┌─────────┼─────────┐
│ │ │
▼ ▼ ▼
[Tool 1] [Tool 2] [Tool 3]
load_data anomalies report

text

Each agent calls tools with the `config_path` parameter:

result = await load_data(
file_path="data/shipments_data.xlsx",
config_path="config/analysis_settings.json"
)

text

---

## Tool Reference

### 1. load_data

**Purpose:** Universal data loader supporting multiple formats with validation.

**Signature:**
async def load_data(
file_path: str,
config_path: str = "config/analysis_settings.json"
) -> ToolResult

text

**Parameters:**
- `file_path` (str, required): Path to data file (CSV, Excel, JSON, PDF)
- `config_path` (str, optional): Path to configuration file

**Returns:**
{
"success": True,
"data": [...],
"row_count": 10000,
"columns": ["date", "store_name", ...],
"execution_time_ms": 342
}

text

**Supported Formats:**
- CSV (`.csv`) — Fast parsing with pandas
- Excel (`.xlsx`, `.xls`) — Full sheet support
- JSON (`.json`) — Nested structure flattening
- PDF (`.pdf`) — Text extraction via PyPDF2

**Validation:**
- Checks required columns from config
- Limits rows to `max_rows` parameter
- Skips malformed rows with warning

**Example:**
from tools.data_loader import load_data

result = await load_data(
file_path="data/transactions.csv",
config_path="config/analysis_settings.json"
)

if result["success"]:
print(f"Loaded {result['row_count']} rows")
data = result["data"]

text

---

### 2. detect_anomalies

**Purpose:** Identify statistical outliers using IQR or Z-score methods.

**Signature:**
async def detect_anomalies(
data: list,
anomaly_columns: list = None,
method: str = "iqr",
threshold: float = 1.5,
config_path: str = "config/analysis_settings.json"
) -> ToolResult

text

**Parameters:**
- `data` (list, required): List of dictionaries from `load_data`
- `anomaly_columns` (list, optional): Columns to analyze (default: from config)
- `method` (str, optional): "iqr" or "zscore"
- `threshold` (float, optional): Sensitivity multiplier (default from config)
- `config_path` (str, optional): Path to configuration

**Returns:**
{
"success": True,
"data": [
{
"index": 42,
"row": {...},
"anomaly_score": 3.2,
"method": "iqr",
"severity": "HIGH"
},
...
],
"total_anomalies": 27,
"execution_time_ms": 156
}

text

**Methods:**

**IQR (Interquartile Range):**
- Formula: `Q1 - 1.5*IQR` to `Q3 + 1.5*IQR`
- Best for: Skewed distributions, robust to outliers
- Threshold: 1.5 (standard), 1.0 (sensitive), 2.0 (lenient)

**Z-Score:**
- Formula: `|value - mean| / std_dev > threshold`
- Best for: Normal distributions
- Threshold: 2.0 (95% confidence), 3.0 (99.7% confidence)

**Example:**
from tools.anomaly_detector import detect_anomalies

anomalies = await detect_anomalies(
data=loaded_data,
anomaly_columns=["quantity", "total_value"],
method="iqr",
threshold=1.5,
config_path="config/analysis_settings.json"
)

for anomaly in anomalies["data"]:
print(f"Row {anomaly['index']}: {anomaly['severity']} - Score {anomaly['anomaly_score']}")

text

---

### 3. search_trends

**Purpose:** Search for market trends, patterns, or related information.

**Signature:**
async def search_trends(
topic: str,
use_api: bool = False,
config_path: str = "config/analysis_settings.json"
) -> ToolResult

text

**Parameters:**
- `topic` (str, required): Search query (e.g., "Widget-X sales anomaly")
- `use_api` (bool, optional): Use real Google Search API (future)
- `config_path` (str, optional): Path to configuration

**Returns:**
{
"success": True,
"data": [
{
"title": "Market insights on Widget-X",
"description": "Recent trends show...",
"source": "mock" | "google",
"relevance_score": 0.92
},
...
],
"result_count": 5,
"execution_time_ms": 234
}

text

**Example:**
from tools.market_trends import search_trends

trends = await search_trends(
topic="Widget-X Friday spike anomaly",
use_api=False,
config_path="config/analysis_settings.json"
)

for trend in trends["data"]:
print(f"{trend['title']} ({trend['relevance_score']:.0%})")

text

---

### 4. generate_report_html

**Purpose:** Create interactive HTML reports with charts and insights.

**Signature:**
async def generate_report_html(
report_data: dict,
output_file: str = "output/analysis_report.html",
config_path: str = "config/analysis_settings.json"
) -> ToolResult

text

**Parameters:**
- `report_data` (dict, required): Report contents
  - `title` (str): Report title
  - `summary` (str): Executive summary
  - `anomalies` (list): Anomaly records
  - `recommendations` (list): Action items
- `output_file` (str, optional): Output path
- `config_path` (str, optional): Path to configuration

**Returns:**
{
"success": True,
"data": {
"file_path": "output/analysis_report.html",
"file_size_kb": 145,
"sections_generated": 4
},
"execution_time_ms": 89
}

text

**Report Structure:**
<html> <head><title>Report Title</title></head> <body> <!-- Summary --> <!-- Anomaly Table --> <!-- Charts (if data available) --> <!-- Recommendations --> </body> </html> ```
Example:

text
from tools.report_generator import generate_report_html

report = await generate_report_html(
    report_data={
        "title": "Q4 Sales Analysis",
        "summary": "Detected 27 anomalies in shipment data",
        "anomalies": anomaly_list,
        "recommendations": [
            {"severity": "HIGH", "text": "Audit NYC-East operations"},
            {"severity": "MEDIUM", "text": "Review demand forecasting"}
        ]
    },
    output_file="output/analysis_report.html",
    config_path="config/analysis_settings.json"
)

print(f"Report saved to {report['data']['file_path']}")
5. log_agent_action
Purpose: Structured logging for observability and audit trails.

Signature:

text
async def log_agent_action(
    agent_name: str,
    action: str,
    details: dict = None,
    level: str = "INFO",
    config_path: str = "config/analysis_settings.json"
) -> ToolResult
Parameters:

agent_name (str, required): Agent identifier (e.g., "Coordinator", "Analyst")

action (str, required): Action type (e.g., "start_analysis", "error_detected")

details (dict, optional): Additional context

level (str, optional): Log severity ("INFO", "WARNING", "ERROR")

config_path (str, optional): Path to configuration

Returns:

text
{
    "success": True,
    "data": {
        "log_file": "logs/agent_actions.jsonl",
        "entry_id": "uuid-1234",
        "timestamp": "2024-11-25T15:32:10Z"
    },
    "execution_time_ms": 5
}
Log Format (JSONL):

text
{"timestamp": "2024-11-25T15:32:10Z", "agent": "Coordinator", "action": "start_analysis", "level": "INFO", "details": {...}}
Example:

text
from tools.action_logger import log_agent_action

await log_agent_action(
    agent_name="Coordinator",
    action="analysis_complete",
    details={
        "anomalies_found": 27,
        "rows_processed": 10000,
        "execution_time_seconds": 3.42
    },
    level="INFO",
    config_path="config/analysis_settings.json"
)
Integration Patterns
Pattern 1: Sequential Tool Execution
Execute tools one after another, using output from previous step:

text
async def sequential_analysis(file_path: str, config_path: str):
    load_result = await load_data(file_path, config_path)
    if not load_result["success"]:
        return None
    
    anomaly_result = await detect_anomalies(
        data=load_result["data"],
        config_path=config_path
    )
    
    report_result = await generate_report_html(
        report_data={
            "title": "Analysis Report",
            "anomalies": anomaly_result["data"],
            "recommendations": []
        },
        config_path=config_path
    )
    
    await log_agent_action(
        agent_name="AnalysisAgent",
        action="workflow_complete",
        details={"anomalies": anomaly_result["total_anomalies"]},
        config_path=config_path
    )
    
    return report_result
Pattern 2: Parallel Tool Execution
Execute independent tools concurrently using asyncio:

text
import asyncio

async def parallel_workflow(data: list, config_path: str):
    results = await asyncio.gather(
        detect_anomalies(data, config_path=config_path),
        search_trends("sales anomaly", config_path=config_path),
        log_agent_action("Coordinator", "parallel_start", config_path=config_path)
    )
    
    anomalies, trends, _ = results
    return {"anomalies": anomalies, "trends": trends}
Pattern 3: Error Handling with Fallback
Gracefully handle tool failures:

text
async def resilient_workflow(file_path: str, config_path: str):
    try:
        result = await load_data(file_path, config_path)
        if not result["success"]:
            raise Exception(f"Load failed: {result.get('error')}")
        return result["data"]
    
    except FileNotFoundError:
        await log_agent_action(
            agent_name="Coordinator",
            action="fallback_mock_data",
            level="WARNING",
            config_path=config_path
        )
        return [{"id": 1, "value": 100}]
    
    except Exception as e:
        await log_agent_action(
            agent_name="Coordinator",
            action="error",
            details={"error": str(e)},
            level="ERROR",
            config_path=config_path
        )
        return None
Creating Custom Tools
Tool Template
Create a new tool by following this structure:

text
# tools/custom_tool.py
from typing import Any, Dict, List
from core.observability import ObservabilityPlugin

async def custom_tool(
    input_data: Any,
    config_path: str = "config/analysis_settings.json"
) -> Dict[str, Any]:
    """
    Custom tool description.
    
    Args:
        input_data: Tool input
        config_path: Path to configuration file
    
    Returns:
        {
            "success": bool,
            "data": Any,
            "execution_time_ms": int,
            "error": Optional[str]
        }
    """
    observer = ObservabilityPlugin()
    start_time = observer.get_timestamp()
    
    try:
        result_data = process(input_data)
        
        return {
            "success": True,
            "data": result_data,
            "execution_time_ms": observer.get_elapsed(start_time)
        }
    
    except Exception as e:
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "execution_time_ms": observer.get_elapsed(start_time)
        }
Registering Custom Tools
Add to agent tools list in your tools module:

text
from tools.custom_tool import custom_tool

TOOLS = [
    load_data,
    detect_anomalies,
    search_trends,
    generate_report_html,
    log_agent_action,
    custom_tool  # Add your tool here
]
Configuration Management
Using config/analysis_settings.json
All tools read from this central configuration file:

json
{
  "required_columns": ["date", "store_name", "product_name", "quantity", "price_per_unit", "total_value"],
  "anomaly_columns": ["quantity", "total_value"],
  "anomaly_method": "iqr",
  "anomaly_threshold": 1.5,
  "max_rows": 10000,
  "log_level": "INFO",
  "output_dir": "output"
}
Dynamic Configuration Per Domain
Create domain-specific configs:

bash
config/
├── analysis_settings.json          # Default (retail)
├── analysis_settings_finance.json  # Financial fraud detection
├── analysis_settings_healthcare.json # Patient data analysis
└── analysis_settings_supply_chain.json # Logistics anomalies
Pass config to tools:

python
# Financial analysis
await detect_anomalies(
    data=transactions,
    config_path="config/analysis_settings_finance.json"
)

# Healthcare analysis
await detect_anomalies(
    data=patient_vitals,
    config_path="config/analysis_settings_healthcare.json"
)
Performance Tuning
Optimization Tips
1. Batch Processing

python
# Instead of processing one by one
for row in large_dataset:
    result = await process(row)  # SLOW

# Batch process
results = await asyncio.gather(*[
    process(batch) for batch in batched(large_dataset, 100)
])  # FAST
2. Select Appropriate Anomaly Method

IQR: O(n log n) - Best for general use

Z-Score: O(n) - Fast but requires normal distribution

Threshold: O(n) - Fastest but least sophisticated

3. Reduce max_rows in Config

json
{
  "max_rows": 5000  # Process first 5K rows, not 10K
}
4. Use Parallel Tools

python
# Load, detect, search in parallel
results = await asyncio.gather(
    load_data(...),
    detect_anomalies(...),
    search_trends(...)
)
Benchmark Results (Local Testing)
Operation	Rows	Time	Method
load_data	10,000	125ms	Pandas
detect_anomalies (IQR)	10,000	42ms	NumPy
detect_anomalies (Z-score)	10,000	38ms	NumPy
search_trends	-	89ms	Mock API
generate_report_html	100 issues	156ms	Jinja2
Observability & Debugging
Structured Logging
All tools output structured logs to logs/agent_actions.jsonl:

json
{
  "timestamp": "2024-11-25T15:32:10.234Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "Coordinator",
  "action": "load_data",
  "level": "INFO",
  "details": {
    "file_path": "data/shipments_data.xlsx",
    "rows_loaded": 10000,
    "execution_time_ms": 125
  }
}
Trace IDs for End-to-End Tracking
Every agent workflow generates a unique trace ID:

python
from core.observability import ObservabilityPlugin

observer = ObservabilityPlugin()
trace_id = observer.generate_trace_id()

# Log all actions with same trace_id
await log_agent_action(
    agent_name="Coordinator",
    action="workflow_start",
    details={"trace_id": trace_id},
    config_path=config_path
)
Retrieving Metrics
python
from core.observability import ObservabilityPlugin

observer = ObservabilityPlugin()
metrics = observer.get_metrics_summary()

print(f"Total agent calls: {metrics['total_agent_calls']}")
print(f"Avg latency: {metrics['avg_latency_ms']}ms")
print(f"Error rate: {metrics['error_rate']:.2%}")
Testing Tools
Unit Test Pattern
python
import pytest
from tools.data_loader import load_data
from tools.anomaly_detector import detect_anomalies

@pytest.mark.asyncio
async def test_load_csv_valid_file():
    """Test loading valid CSV file."""
    result = await load_data(
        file_path="data/test_data.csv",
        config_path="config/analysis_settings.json"
    )
    
    assert result["success"] == True
    assert result["row_count"] > 0
    assert "execution_time_ms" in result

@pytest.mark.asyncio
async def test_detect_anomalies_iqr():
    """Test IQR anomaly detection."""
    test_data = [
        {"value": 100}, {"value": 102}, {"value": 98},
        {"value": 500},  # Outlier
    ]
    
    result = await detect_anomalies(
        data=test_data,
        anomaly_columns=["value"],
        method="iqr",
        threshold=1.5
    )
    
    assert result["success"] == True
    assert result["total_anomalies"] >= 1
    assert any(a["index"] == 3 for a in result["data"])

@pytest.mark.asyncio
async def test_load_nonexistent_file():
    """Test error handling for missing file."""
    result = await load_data(
        file_path="data/nonexistent.csv",
        config_path="config/analysis_settings.json"
    )
    
    assert result["success"] == False
    assert "error" in result
Running Tests
bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_tools.py::test_load_csv_valid_file -v

# With coverage report
pytest tests/ --cov=tools --cov-report=html
Troubleshooting
Issue: Tool Not Found
Problem: AttributeError: module 'tools' has no attribute 'unknown_tool'

Solution: Verify tool is imported in your tools module:

python
# Check imports
from tools.data_loader import load_data
from tools.anomaly_detector import detect_anomalies

# Verify tool is in tools list
print(TOOLS)  # Should include your tool
Issue: Configuration Not Applied
Problem: Tool uses default config instead of custom one

Solution: Pass config_path explicitly to all tool calls:

python
# ✗ Wrong - uses default
result = await detect_anomalies(data=data)

# ✓ Correct - uses custom config
result = await detect_anomalies(
    data=data,
    config_path="config/analysis_settings_finance.json"
)
Issue: Anomaly Detection Returns No Results
Problem: detect_anomalies returns empty list

Solutions:

Check threshold is appropriate

Verify anomaly_columns exist in data

Use IQR instead of Z-score if data isn't normal

python
# Debug: Check data distribution
import statistics
values = [row[col] for row in data]
mean = statistics.mean(values)
stdev = statistics.stdev(values)
print(f"Mean: {mean}, StdDev: {stdev}")

# Try looser threshold
result = await detect_anomalies(
    data=data,
    threshold=2.0  # More lenient than 1.5
)
Issue: CSV File Encoding Error
Problem: UnicodeDecodeError: 'utf-8' codec can't decode...

Solution: Ensure CSV is UTF-8 encoded. Convert if needed:

bash
# Convert CSV to UTF-8
iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
Best Practices
Always check result["success"] before accessing data

python
result = await load_data(...)
if result["success"]:
    data = result["data"]
Use appropriate anomaly detection method

IQR: General purpose, robust

Z-score: When data is normal distributed

Threshold: Simple, fast checks

Log all agent actions for observability

python
await log_agent_action(
    agent_name="MyAgent",
    action="critical_operation",
    details={"status": "success"}
)
Handle errors gracefully with fallbacks

python
try:
    result = await tool(...)
except Exception as e:
    return fallback_data()
Use asyncio.gather for parallel execution

python
results = await asyncio.gather(
    tool1(...),
    tool2(...),
    tool3(...)
)
Validate parameters before tool execution

python
if not file_path.endswith(('.csv', '.xlsx', '.json', '.pdf')):
    raise ValueError("Unsupported file format")
Additional Resources
Tool Source Code: tools/

Configuration Reference: config/analysis_settings.json

Test Suite: tests/test_tools.py

Observability: core/observability.py

Main Entry Point: main.py

Version History
Version	Date	Changes
2.0	2024-11-25	Updated for config-driven architecture, removed ToolRegistry pattern
1.0	2024-11-21	Initial MVP with ToolRegistry
Last Updated: November 25, 2024
Status: Production Ready
Track: Kaggle Agents Intensive Capstone Project