def generate_report_html(analysis_result, recommendation_result, critique_result, summary, output_path=None):
    """
    Generate HTML report from agent results.
    Arguments:
        analysis_result: dict/str (output from Analyst agent)
        recommendation_result: dict/str (output from Recommender agent)
        critique_result: dict/str (output from Critic agent)
        summary: dict/str (final summary from Coordinator agent)
        output_path: str (optional — path to save html)
    Returns:
        str: HTML content
    """
    html = "<html><head><title>LLM Capstone Analysis Report</title></head><body>"
    html += "<h1>Business Analysis Report</h1>"
    html += "<h2>Analysis</h2><pre>{}</pre>".format(str(analysis_result))
    html += "<h2>Recommendations</h2><pre>{}</pre>".format(str(recommendation_result))
    html += "<h2>Critique</h2><pre>{}</pre>".format(str(critique_result))
    html += "<h2>Final Summary</h2><pre>{}</pre>".format(str(summary))
    html += "</body></html>"
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    return html
