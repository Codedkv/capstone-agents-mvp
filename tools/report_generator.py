from .base_tool import BaseTool
import os

class ReportGeneratorTool(BaseTool):
    def __init__(self):
        super().__init__("generate_report_html", "Generate HTML report from analysis results")

    async def execute(self, report_data, output_file=None):
        try:
            title = report_data.get("title", "Report")
            issues = report_data.get("issues", [])
            recommendations = report_data.get("recommendations", [])

            html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; }}
        ul {{ line-height: 1.6; }}
        .severity-high {{ color: red; font-weight: bold; }}
        .severity-medium {{ color: orange; }}
        .severity-low {{ color: green; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <h2>Issues Detected</h2>
    <ul>
"""
            for issue in issues:
                severity = issue.get('severity', 'UNKNOWN')
                description = issue.get('description', 'No description')
                severity_class = f"severity-{severity.lower()}"
                html += f'        <li class="{severity_class}">{description} <strong>(Severity: {severity})</strong></li>\n'

            html += """    </ul>
    <h2>Recommendations</h2>
    <ul>
"""
            for rec in recommendations:
                html += f'        <li>{rec}</li>\n'

            html += """    </ul>
</body>
</html>"""

            if output_file:
                os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(html)
                file_saved = True
                file_path = os.path.abspath(output_file)
            else:
                file_saved = False
                file_path = None

            return type("Result", (), {
                "success": True,
                "data": {
                    "html": html,
                    "file_saved": file_saved,
                    "file_path": file_path
                },
                "error": None
            })()

        except Exception as e:
            return type("Result", (), {
                "success": False,
                "data": None,
                "error": f"Report generation failed: {e}"
            })()
