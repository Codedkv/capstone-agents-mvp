# 🚀 Capstone-Agents-MVP

**Multi-Agent Business Analytics System Powered by Google Gemini 2.5 Flash**

[![Kaggle Competition](https://img.shields.io/badge/Kaggle-Agents%20Intensive-20BEFF?logo=kaggle&logoColor=white)](https://www.kaggle.com/competitions/agents-intensive-capstone-project)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Transform raw business data into actionable insights in seconds.** This autonomous multi-agent system detects anomalies, identifies patterns, and generates strategic recommendations — all without manual intervention.

---

## 🎯 **What Makes This Special?**

### **Autonomous Intelligence at Scale**
Five specialized AI agents collaborate to analyze your data end-to-end:
- **📊 DataLoader Agent** — Ingests CSV, Excel, JSON, and PDF files with smart validation
- **🔍 Analyst Agent** — Detects anomalies using IQR and Z-score methods across multiple metrics
- **📈 Recommender Agent** — Generates strategic recommendations based on discovered patterns
- **🎭 Coordinator Agent** — Orchestrates the entire workflow seamlessly
- **✅ Critic Agent** — Quality-checks outputs and validates insights

### **Config-Driven Flexibility**
**Zero code changes needed** to adapt to your domain:
{
"required_columns": ["date", "store_name", "product_name", "quantity", "price_per_unit"],
"anomaly_columns": ["quantity", "total_value"],
"anomaly_method": "iqr",
"anomaly_threshold": 1.5,
"max_rows": 10000
}

text
Switch from retail analytics to financial fraud detection by just editing the config file.

### **Real-World Use Cases**
- 🛒 **E-commerce:** Detect inventory anomalies and predict stockouts
- 💰 **Finance:** Identify fraudulent transactions and unusual spending patterns
- 🏭 **Supply Chain:** Monitor shipment delays and logistics bottlenecks
- 🏥 **Healthcare:** Analyze patient data for outliers and treatment patterns
- 📞 **Customer Support:** Find spikes in complaint volumes and root causes

### **Enterprise-Grade Observability**
Built-in ADK-compliant monitoring:
- Trace every agent decision with unique trace IDs
- Track performance metrics (latency, success rate, error rate)
- Export structured logs for compliance and auditing
- Visualize agent interactions for debugging

---

## 🏗️ **Architecture**

┌─────────────────────────────────────────────────────────────┐
│ Coordinator Agent (LLM) │
│ Orchestrates workflow & manages context │
└────────────────────┬────────────────────────────────────────┘
│
┌────────────┼────────────┐
│ │ │
▼ ▼ ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ DataLoader │ │ Analyst │ │ Recommender │
│ Agent │ │ Agent │ │ Agent │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
│ │ │
▼ ▼ ▼
[Tools] [Tools] [Tools]
load_data detect_anomalies generate_report
search_trends search_trends
│
▼
┌──────────────┐
│ Critic │
│ Agent │
└──────────────┘

text

**Technology Stack:**
- **LLM:** Google Gemini 2.5 Flash (function calling, async)
- **Orchestration:** Custom LLM Agent framework with shared context
- **Data Processing:** Pandas, NumPy, PyPDF2, openpyxl
- **Observability:** ADK-style traces and metrics
- **Deployment:** Kaggle Notebooks (fully reproducible)

---

## ⚡ **Quick Start**

### **1. Clone & Install**
git clone https://github.com/Codedkv/capstone-agents-mvp.git
cd capstone-agents-mvp
pip install -r requirements.txt

text

### **2. Set API Key**
export GEMINI_API_KEY="your_google_api_key_here"

text

### **3. Run Analysis**
python main.py

text

**That's it!** The system will:
1. Load `data/shipments_data.xlsx` (10K rows)
2. Detect anomalies in `quantity` and `total_value` columns
3. Generate insights and recommendations
4. Export HTML report to `output/analysis_report.html`

---

## 🎨 **Configuration Examples**

### **Retail Analytics**
{
"required_columns": ["date", "store_name", "product_name", "quantity", "price_per_unit", "total_value"],
"anomaly_columns": ["quantity", "total_value"],
"anomaly_method": "iqr",
"anomaly_threshold": 1.5,
"max_rows": 50000
}

text

### **Financial Fraud Detection**
{
"required_columns": ["transaction_id", "user_id", "amount", "timestamp", "merchant"],
"anomaly_columns": ["amount"],
"anomaly_method": "zscore",
"anomaly_threshold": 3.0,
"max_rows": 100000
}

text

### **Healthcare Monitoring**
{
"required_columns": ["patient_id", "vitals_timestamp", "heart_rate", "blood_pressure", "temperature"],
"anomaly_columns": ["heart_rate", "blood_pressure"],
"anomaly_method": "iqr",
"anomaly_threshold": 2.0,
"max_rows": 20000
}

text

---

## 🛠️ **Key Features**

### **1. Multi-Format Data Ingestion**
- **CSV:** High-speed parsing with schema validation
- **Excel (.xlsx, .xls):** Full support via pandas
- **JSON:** Nested structure flattening
- **PDF:** Text extraction for NLP-based analysis

### **2. Advanced Anomaly Detection**
- **IQR Method:** Robust to outliers, ideal for skewed distributions
- **Z-Score Method:** Parametric approach for normally distributed data
- **Multi-Column Scanning:** Simultaneously check multiple metrics
- **Configurable Thresholds:** Tune sensitivity per use case

### **3. Intelligent Pattern Recognition**
- Identify recurring anomaly clusters (e.g., "every Monday at 3 PM")
- Correlate anomalies across dimensions (e.g., "Store A + Product X")
- Surface hidden trends invisible to human analysts

### **4. Actionable Recommendations**
- Prioritized by severity (HIGH, MEDIUM, LOW)
- Contextualized with business impact estimates
- Exportable to HTML, JSON, or PDF formats

### **5. Production-Ready Observability**
from core.observability import ObservabilityPlugin

observer = ObservabilityPlugin(log_dir="./logs")
metrics = observer.get_metrics_summary()
print(metrics)

Output:
{
"total_agent_calls": 15,
"total_tool_calls": 8,
"error_count": 0,
"avg_latency_ms": 342,
"success_rate": 1.0,
"anomalies_found": 27
}
text

---

## 📊 **Sample Output**

**Input:** `data/shipments_data.xlsx` (10,000 rows)

**Console Output:**
=== FINAL LLM PIPELINE RESULT ===
✓ Loaded 10,000 rows from shipments_data.xlsx
✓ Detected 27 anomalies in quantity and total_value
✓ Identified 3 high-priority patterns:

Store "NYC-East" has 12 extreme outliers (>3x normal)

Product "Widget-X" shows recurring spikes every Friday

Total value anomalies correlate with quantity anomalies (0.87 correlation)

RECOMMENDATIONS:
[HIGH] Audit NYC-East inventory management process
[MEDIUM] Investigate Widget-X demand forecasting model
[LOW] Review weekend staffing levels

Report saved to: output/analysis_report.html
text

**Generated Report:**
- Interactive HTML dashboard with charts
- Downloadable anomaly list (CSV)
- Trend visualizations

---

## 🧪 **Evaluation & Testing**

### **Run Test Suite**
pytest tests/ -v

text

### **Evaluate Agent Performance**
python evaluation/agent_evaluator.py

text

**Metrics Tracked:**
- **Accuracy:** % of correctly identified anomalies
- **Precision/Recall:** For anomaly classification
- **Latency:** Average response time per agent
- **Error Rate:** Failed tool calls or exceptions

---

## 📦 **Project Structure**

capstone-agents-mvp/
├── agents/ # LLM agent implementations
│ ├── coordinator_llm.py
│ ├── agent_roles_llm.py
│ └── ...
├── core/ # Base frameworks
│ ├── agent_base_llm.py
│ ├── llm_client.py
│ ├── observability.py
│ └── context.py
├── tools/ # Reusable tool functions
│ ├── data_loader.py
│ ├── anomaly_detector.py
│ ├── market_trends.py
│ ├── report_generator.py
│ └── action_logger.py
├── config/ # Config-driven settings
│ └── analysis_settings.json
├── evaluation/ # Testing & metrics
│ ├── agent_evaluator.py
│ └── test_cases.py
├── data/ # Sample datasets
│ └── shipments_data.xlsx
├── notebooks/ # Kaggle deployment
│ └── capstone_demo_final.ipynb
├── output/ # Generated reports
├── logs/ # Observability traces
├── main.py # Entry point
└── requirements.txt

text

---

## 🚀 **Deploy to Kaggle**

### **Step 1: Upload Notebook**
1. Open [Kaggle Notebooks](https://www.kaggle.com/code)
2. Upload `notebooks/capstone_demo_final.ipynb`
3. Set kernel to **Python 3.10+** with **GPU (optional)**

### **Step 2: Set API Key**
import os
os.environ["GEMINI_API_KEY"] = "your_key_here"

text

### **Step 3: Run All Cells**
The notebook will:
- Install dependencies
- Load sample data
- Execute full agent pipeline
- Display results inline

**Reproducibility Guaranteed:** All paths are relative, no local file dependencies.

---

## 🔬 **Advanced Capabilities**

### **Near Real-Time Database Analysis**
Connect to live databases (PostgreSQL, MySQL, BigQuery):
import pandas as pd
from sqlalchemy import create_engine

Connect to database
engine = create_engine("postgresql://user:pass@host:5432/dbname")
df = pd.read_sql_query("SELECT * FROM transactions WHERE date > NOW() - INTERVAL '7 days'", engine)

Export to CSV for analysis
df.to_csv("data/live_transactions.csv", index=False)

Run agent pipeline
python main.py

text

### **Custom Tool Integration**
Add domain-specific tools easily:
tools/custom_tool.py
def validate_business_rules(data, config_path):
"""Check if data violates custom business logic."""
# Your logic here
return {"status": "success", "violations": []}

Register in agents/agent_roles_llm.py
ANALYST_TOOLS.append(validate_business_rules)

text

### **Multi-Language Support**
Config files support internationalization:
{
"language": "en",
"report_title": "Business Analytics Report",
"severity_labels": {
"HIGH": "Critical",
"MEDIUM": "Warning",
"LOW": "Informational"
}
}

text

---

## 🏆 **Competition Alignment**

**Kaggle Agents Intensive Capstone Project Requirements:**

✅ **Multi-Agent Architecture** — 5 specialized agents with clear roles  
✅ **Tool Integration** — 5 production-ready tools with function calling  
✅ **ADK Compliance** — Observability, metrics, error handling  
✅ **Config-Driven Design** — Zero-code adaptation to new domains  
✅ **Evaluation Framework** — Automated testing and metrics collection  
✅ **Reproducibility** — Kaggle Notebook with deterministic results  
✅ **Documentation** — Comprehensive README and code comments  

---

## 📚 **Learn More**

- **Kaggle Course Materials:** [5 Days of AI Agents](https://www.kaggle.com/whitepaper-introduction-to-agents)
- **Google Gemini Docs:** [Generative AI SDK](https://ai.google.dev/docs)
- **ADK Framework:** [Agent Developer Kit](https://www.kaggle.com/whitepaper-agent-quality)

---

## 🤝 **Contributing**

We welcome contributions! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit with clear messages (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 **License**

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- **Google & Kaggle** for the Agents Intensive Course
- **Gemini 2.5 Flash** for blazing-fast LLM inference
- **Open-source community** for foundational libraries

---

## 📧 **Contact**

**Author:** Codedkv  
**GitHub:** [Codedkv](https://github.com/Codedkv)  
**Project Link:** [capstone-agents-mvp](https://github.com/Codedkv/capstone-agents-mvp)

---

**⭐ Star this repo if you find it useful! ⭐**