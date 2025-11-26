import os

def generate_report_html(analysis_result, recommendation_result, critique_result, summary, output_path=None):
    """
    Generate HTML report from agent results and save to file.
    Arguments:
        analysis_result: dict/str
        recommendation_result: dict/str
        critique_result: dict/str
        summary: dict/str
        output_path: str (path to save html, e.g., 'output/analysis_report.html')
    Returns:
        dict: Status of generation
    """
    html = "<html><head><title>LLM Capstone Analysis Report</title>"
    html += "<style>body{font-family: sans-serif; max-width: 800px; margin: auto; padding: 20px;}"
    html += "h1, h2{color: #2c3e50;} pre{background: #f4f4f4; padding: 10px; border-radius: 5px; white-space: pre-wrap;}</style>"
    html += "</head><body>"
    html += "<h1>Business Analysis Report</h1>"
    
    # Using generic string representation to avoid serialization issues
    html += "<h2>1. Analysis Findings</h2>"
    html += f"<pre>{str(analysis_result)}</pre>"
    
    html += "<h2>2. Strategic Recommendations</h2>"
    html += f"<pre>{str(recommendation_result)}</pre>"
    
    html += "<h2>3. Critique & Quality Control</h2>"
    html += f"<pre>{str(critique_result)}</pre>"
    
    html += "<h2>4. Executive Summary</h2>"
    html += f"<pre>{str(summary)}</pre>"
    
    html += "</body></html>"
    
    if output_path:
        try:
            # Ensure directory exists to prevent FileNotFoundError
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            return {
                "status": "success", 
                "message": f"Report saved to {output_path}",
                "path": output_path
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    return {
        "status": "success",
        "message": "Report generated in memory (no path provided)",
        "content_preview": html[:100] + "..."
    }
