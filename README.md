# Multi-Agent Business Analytics System (Capstone-Agents-MVP)

## 🏆 Project Overview
This project is a **Config-Driven Multi-Agent System** powered by **Google Gemini 2.5 Flash**. It automates the end-to-end process of business data analysis: from data ingestion and anomaly detection to strategic recommendations and critical review.

Designed for the **Kaggle Agents Intensive Capstone**, this system demonstrates how autonomous LLM agents can orchestrate complex analytical workflows using specialized tools without hallucinating data.

---

## 🚀 Key Features

### 1. 🧠 5-Agent Architecture
- **Coordinator:** Orchestrates the workflow and ensures final report generation.
- **DataLoader:** Validates file schemas and prepares data pointers.
- **Analyst:** Uses statistical tools (IQR, Z-Score) to detect anomalies and trends.
- **Recommender:** Translates analytical findings into business strategies.
- **Critic:** Reviews the entire chain for logical consistency and hallucinations.

### 2. ⚡ Efficient "Filepath Passing" Logic
Instead of passing raw text (expensive on tokens), agents pass **filepaths**. Tools read the data directly from disk, returning only high-level summaries to the LLM context. This allows processing large datasets (10k+ rows) within standard context limits.

### 3. ⚙️ Config-Driven Analysis
All analytical parameters are controlled via `config/analysis_settings.json`. No code changes required to switch from "Sales Data" to "IoT Sensor Data".

### 4. 🛡️ Double-Safety Execution
The system features programmatic fallbacks to ensure the final HTML report is generated even if the LLM agent fails to call the save tool.

---

## 🛠️ Technical Stack
- **LLM:** Google Gemini 2.5 Flash
- **Language:** Python 3.10+
- **Libraries:** `google-generativeai`, `pandas`, `openpyxl`
- **Output:** HTML Report with CSS styling

---

## 📥 Installation & Usage

1. **Clone the repository:**
git clone https://github.com/Codedkv/capstone-agents-mvp.git
cd capstone-agents-mvp

text

2. **Install dependencies:**
pip install -r requirements.txt

text

3. **Set up API Key:**
Create a `.env` file:
GEMINI_API_KEY=your_api_key_here

text

4. **Run the Pipeline:**
python main.py

text

5. **View Results:**
Open `output/analysis_report.html` in your browser.

---

## 🔮 Future Roadmap (Enterprise Scaling)

This MVP sets the foundation for a scalable **SaaS Analytics Platform**. Future development phases include:

### Phase 2: The "Control Tower" Admin Panel
- **Unified UI:** A React/Streamlit dashboard for non-technical users.
- **Drag & Drop:** File receiver supporting `.csv`, `.xlsx`, `.pdf`, `.json`.
- **Live API Config:** Input Gemini API keys directly in the interface.
- **Interactive Reporting:** A split-screen view showing the chat log alongside the rendered HTML report.
- **Multi-Format Export:** Save reports as PDF, DOCX, or Send via Email.

### Phase 3: Long-Term Anomaly Intelligence
- **Anomaly Database:** Store every detected anomaly in a persistent SQL database (PostgreSQL).
- **Pattern Recognition:** Analyze anomalies over months/years to detect seasonality or systemic degradation.
- **Cross-Dataset Correlation:** Find links between anomalies in "Sales" and "Logistics" datasets uploaded separately.

---

## 📂 Project Structure
├── agents/ # LLM Agent definitions
├── config/ # Configuration files (prompts, settings)
├── core/ # Base classes and LLM client
├── data/ # Input datasets
├── output/ # Generated reports
├── tools/ # Python tools (Analysis, Loading, Logging)
├── main.py # Entry point
└── requirements.txt # Dependencies

📜 License
This project is licensed under the MIT License. You are free to use, modify, and distribute this software for educational and professional purposes.

🙏 Acknowledgments
Developed for the Google x Kaggle AI Agents Intensive 2025.

Powered by Google Gemini 2.5 Flash.

Special thanks to the Kaggle team for the DeepLearning.AI agentic workflow resources.