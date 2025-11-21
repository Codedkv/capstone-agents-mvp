# 🔧 TOOLS INTEGRATION GUIDE

## Day 2 MVP: Production-Ready Tools System

Complete guide for integrating tools with Coordinator and Sub-Agents.

---

## 📦 TOOLS OVERVIEW

### Available Tools (MVP)

| Tool | Type | Status | Purpose |
|------|------|--------|---------|
| `load_csv_data` | Data Loader | ✅ Production | Load & validate CSV files |
| `detect_anomalies` | Analytics | ✅ Production | Statistical anomaly detection (IQR, Z-score) |
| `search_market_trends` | Search | 🔄 Mock | Market trends search (real API in Day 3) |
| `generate_report_html` | Reporting | ✅ Production | Generate HTML reports |
| `log_agent_action` | Logging | ✅ Production | Structured action logging |

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────┐
│    COORDINATOR AGENT            │
│    (Uses ToolRegistry)          │
└────────────┬────────────────────┘
             │
             ▼
┌──────────────────────────────────┐
│    TOOL REGISTRY                 │
│  (Manages 5 tools)               │
└───┬──┬──┬──┬──┬──────────────────┘
    │  │  │  │  │
    ▼  ▼  ▼  ▼  ▼
  [Load] [Detect] [Search] [Report] [Log]
  CSV    Anomalies Trends  HTML     Action
```

---

## 🚀 QUICK START

### 1. Import and Initialize

```python
# Import tool classes
from tools import (
    DataLoaderTool,
    AnomalyDetectorTool,
    MarketTrendsTool,
    ReportGeneratorTool,
    ActionLoggerTool
)
from tools import ToolRegistry

# Create registry
registry = ToolRegistry()

# Register all tools
registry.register(DataLoaderTool())
registry.register(AnomalyDetectorTool())
registry.register(MarketTrendsTool())
registry.register(ReportGeneratorTool())
registry.register(ActionLoggerTool())

print(f"Registered {len(registry.list_tool_names())} tools")
# Output: Registered 5 tools
```

### 2. Use Tools Directly

```python
import asyncio

async def main():
    # Load data
    loader = DataLoaderTool()
    result = await loader.execute(
        filepath="data/sample_business_metrics.csv",
        validate=True
    )
    
    if result.success:
        data = result.data
        print(f"Loaded {len(data)} rows")
    else:
        print(f"Error: {result.error}")

asyncio.run(main())
```

### 3. Integrate with Coordinator

```python
class CoordinatorAgent:
    """Main coordinator with tool support."""
    
    def __init__(self, tool_registry):
        self.registry = tool_registry
        self.logger = self.registry.get_tool("log_agent_action")
    
    async def execute_analysis(self, filepath):
        """Execute analysis using tools."""
        
        # 1. Log action
        await self.logger.execute(
            agent_name="Coordinator",
            action="start_analysis",
            details={"file": filepath},
            level="INFO"
        )
        
        # 2. Load data
        loader = self.registry.get_tool("load_csv_data")
        load_result = await loader.execute(filepath=filepath)
        
        if not load_result.success:
            await self.logger.execute(
                agent_name="Coordinator",
                action="error",
                details={"error": load_result.error},
                level="ERROR"
            )
            return
        
        # 3. Detect anomalies
        detector = self.registry.get_tool("detect_anomalies")
        anomaly_result = await detector.execute(
            data=extract_metric(load_result.data, "revenue"),
            method="iqr"
        )
        
        # 4. Generate report
        reporter = self.registry.get_tool("generate_report_html")
        report_result = await reporter.execute(
            report_data={
                "title": "Analysis Report",
                "issues": format_issues(anomaly_result.data),
                "recommendations": []
            },
            output_file="output/report.html"
        )
        
        # 5. Log completion
        await self.logger.execute(
            agent_name="Coordinator",
            action="analysis_complete",
            details={"status": "success"},
            level="INFO"
        )
        
        return report_result
```

---

## 🔌 TOOL INTEGRATION PATTERNS

### Pattern 1: Sequential Tool Execution

```python
async def sequential_workflow():
    """Execute tools in sequence."""
    
    # Step 1: Load
    load_result = await load_tool.execute(filepath="data.csv")
    
    # Step 2: Process (use output of step 1)
    process_result = await process_tool.execute(data=load_result.data)
    
    # Step 3: Report (use output of step 2)
    report_result = await report_tool.execute(
        report_data=process_result.data
    )
    
    return report_result
```

### Pattern 2: Parallel Tool Execution

```python
import asyncio

async def parallel_workflow():
    """Execute independent tools in parallel."""
    
    # All three tools can run independently
    results = await asyncio.gather(
        load_tool.execute(filepath="data.csv"),
        search_tool.execute(topic="Sales"),
        logger_tool.execute(agent_name="Test", action="start")
    )
    
    return results
```

### Pattern 3: Error Handling with Fallback

```python
async def resilient_workflow():
    """Execute with error handling and fallbacks."""
    
    try:
        result = await load_tool.execute(filepath="data.csv")
    except Exception as e:
        logger.execute(
            agent_name="Error Handler",
            action="fallback",
            details={"error": str(e)},
            level="WARNING"
        )
        # Use mock data
        result = ToolResult(success=True, data=mock_data)
    
    return result
```

---

## 📊 TOOL USAGE EXAMPLES

### Example 1: Complete Analysis Workflow

```python
async def complete_analysis(filepath):
    """End-to-end analysis using all tools."""
    
    # 1. Load data
    loader = registry.get_tool("load_csv_data")
    data_result = await loader.execute(filepath=filepath)
    
    if not data_result.success:
        return None
    
    # 2. Extract revenue metric
    revenue = [float(row.get("revenue", 0)) for row in data_result.data]
    
    # 3. Detect anomalies
    detector = registry.get_tool("detect_anomalies")
    anomaly_result = await detector.execute(
        data=revenue,
        method="iqr",
        threshold=1.5
    )
    
    # 4. Search related trends
    searcher = registry.get_tool("search_market_trends")
    if anomaly_result.data["count"] > 0:
        trend_result = await searcher.execute(
            topic="Sales anomaly"
        )
    
    # 5. Generate report
    reporter = registry.get_tool("generate_report_html")
    issues = format_anomalies_to_issues(anomaly_result.data)
    
    report_result = await reporter.execute(
        report_data={
            "title": f"Analysis: {filepath}",
            "issues": issues,
            "recommendations": generate_recommendations(issues)
        }
    )
    
    # 6. Log completion
    logger = registry.get_tool("log_agent_action")
    await logger.execute(
        agent_name="AnalysisWorkflow",
        action="completed",
        details={
            "anomalies": anomaly_result.data["count"],
            "report_file": report_result.data.get("file_path")
        }
    )
    
    return report_result
```

### Example 2: Using Tools with Sub-Agents

```python
class HistoricalAnalyzerAgent:
    """Sub-agent using tools."""
    
    def __init__(self, tool_registry):
        self.registry = tool_registry
        self.loader = tool_registry.get_tool("load_csv_data")
        self.detector = tool_registry.get_tool("detect_anomalies")
        self.logger = tool_registry.get_tool("log_agent_action")
    
    async def analyze(self, filepath):
        """Analyze historical data."""
        
        # Load data
        data_result = await self.loader.execute(filepath=filepath)
        
        if not data_result.success:
            await self.logger.execute(
                agent_name="HistoricalAnalyzer",
                action="error",
                details={"error": data_result.error},
                level="ERROR"
            )
            return None
        
        # Analyze each metric
        results = {}
        for metric in ["revenue", "costs", "customers"]:
            metric_data = [float(row.get(metric, 0)) for row in data_result.data]
            
            anomaly_result = await self.detector.execute(
                data=metric_data,
                method="iqr"
            )
            
            results[metric] = anomaly_result.data
        
        # Log analysis
        await self.logger.execute(
            agent_name="HistoricalAnalyzer",
            action="analysis_complete",
            details={
                "metrics": len(results),
                "total_anomalies": sum(r["count"] for r in results.values())
            }
        )
        
        return results
```

---

## 🔄 TOOL REGISTRY MANAGEMENT

### Register Tools

```python
registry = ToolRegistry()

# Register individual tool
registry.register(DataLoaderTool())

# Verify registration
assert registry.has_tool("load_csv_data")

# Get tool
loader = registry.get_tool("load_csv_data")
```

### List All Tools

```python
# List tool names
tool_names = registry.list_tool_names()
print(tool_names)
# Output: ['load_csv_data', 'detect_anomalies', ...]

# List tool specifications
specs = registry.list_tools()
for spec in specs:
    print(f"{spec['name']}: {spec['description']}")
```

### Tool Specifications

```python
# Get tool spec
tool = registry.get_tool("load_csv_data")
spec = tool.to_dict()

print(spec)
# {
#     "name": "load_csv_data",
#     "description": "...",
#     "parameters": [...]
# }
```

---

## 🧪 TESTING TOOLS

### Unit Test Pattern

```python
import pytest

@pytest.mark.asyncio
async def test_load_csv_tool():
    """Test DataLoaderTool."""
    tool = DataLoaderTool()
    result = await tool.execute(filepath="test_data.csv")
    
    assert result.success
    assert len(result.data) > 0
    assert result.execution_time_ms > 0

@pytest.mark.asyncio
async def test_detect_anomalies_tool():
    """Test AnomalyDetectorTool."""
    tool = AnomalyDetectorTool()
    result = await tool.execute(
        data=[100, 102, 98, 500],
        method="iqr"
    )
    
    assert result.success
    assert result.data["count"] > 0  # 500 should be detected
```

### Run Tests

```bash
# Run all tests
pytest tests/test_tools.py -v

# Run specific test
pytest tests/test_tools.py::TestDataLoaderTool::test_load_valid_csv -v

# With coverage
pytest tests/test_tools.py --cov=tools --cov-report=html
```

---

## ⚙️ CONFIGURATION

### Tool Parameters

Each tool has documented parameters in `config/tool_registry.json`.

```json
{
  "load_csv_data": {
    "parameters": {
      "filepath": {
        "type": "string",
        "required": true,
        "example": "data/sample_business_metrics.csv"
      },
      "validate": {
        "type": "boolean",
        "required": false,
        "default": true
      }
    }
  }
}
```

### Tool Specifications

Retrieve tool specs programmatically:

```python
tool = registry.get_tool("load_csv_data")
params = tool.get_parameters()

for param in params:
    print(f"{param.name}: {param.description}")
    print(f"  Type: {param.type}")
    print(f"  Required: {param.required}")
```

---

## 📈 TOOL PERFORMANCE

### Benchmarks (Local Testing)

| Tool | Operation | Time | Data Size |
|------|-----------|------|-----------|
| load_csv_data | Load CSV | ~10ms | 1,000 rows |
| detect_anomalies | IQR detection | ~5ms | 10,000 points |
| search_market_trends | Search (mock) | ~2ms | - |
| generate_report_html | Generate HTML | ~20ms | 100 issues |
| log_agent_action | Write JSONL | ~1ms | 1 entry |

### Optimization Tips

```python
# Batch operations
results = await asyncio.gather(
    detector.execute(data1),
    detector.execute(data2),
    detector.execute(data3)
)

# Use appropriate method
# IQR: O(n log n), best for general use
# Z-score: O(n), needs normal distribution
# Threshold: O(n), fastest but least robust
```

---

## 🔮 FUTURE INTEGRATION (Day 3+)

### Google Search API

```python
# Planned for Day 3:
search_result = await search_tool.execute(
    topic="Sales decline",
    use_api="google"  # Will use real Google Search API
)
```

### Gemini API Integration

```python
# Planned for Day 3:
result = await recommender.execute(
    issues=anomalies,
    use_model="gemini"  # Real Gemini reasoning
)
```

---

## 📞 TROUBLESHOOTING

### Issue: Tool Not Found

```python
# Problem
tool = registry.get_tool("unknown_tool")  # Returns None

# Solution
if not registry.has_tool("unknown_tool"):
    print("Tool not registered!")
    print(f"Available: {registry.list_tool_names()}")
```

### Issue: Parameter Validation Error

```python
# Problem
result = await tool.execute(invalid_param=123)

# Solution
try:
    tool.validate_parameters({"filepath": "data.csv"})
    result = await tool.execute(filepath="data.csv")
except ToolExecutionError as e:
    print(f"Validation failed: {e}")
```

### Issue: CSV Not Found

```python
# Problem
result = await loader.execute(filepath="nonexistent.csv")
# result.success == False

# Solution
import os
if os.path.exists(filepath):
    result = await loader.execute(filepath=filepath)
else:
    print(f"File not found: {filepath}")
```

---

## 📝 BEST PRACTICES

1. **Always check result.success** before using result.data
2. **Use appropriate anomaly detection method**:
   - IQR: General purpose, robust
   - Z-score: When distribution is normal
   - Threshold: Simple, fast checks
3. **Log all agent actions** for observability
4. **Handle errors gracefully** with fallbacks
5. **Use async/await** for concurrent execution
6. **Validate parameters** before tool execution

---

## 📚 ADDITIONAL RESOURCES

- `config/tool_registry.json` — Complete tool specifications
- `tests/test_tools.py` — Test examples and patterns
- Individual tool modules — Detailed docstrings and examples
- `README.md` — Project overview

---

**Created:** 2024-11-21  
**Status:** ✅ MVP Complete  
**Next:** Day 3 - Real API Integration  
**Track:** Kaggle Agents Intensive
