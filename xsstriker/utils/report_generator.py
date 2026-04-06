import json
import datetime
import os

class ReportGenerator:
    """Layer 4: Generates JSON and HTML reports based on XSS scan results."""
    def __init__(self, vulnerabilities=None, ai_metrics=None):
        self.vulnerabilities = vulnerabilities if vulnerabilities else []
        self.ai_metrics = ai_metrics if ai_metrics else {}
        self.report_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_json(self, filepath="xsstriker/reports/report.json"):
        """Generate a technical report in JSON format."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        report = {
            "title": "XSSStriker AI Scan Report",
            "timestamp": self.report_time,
            "vulnerabilities": self.vulnerabilities,
            "ai_metrics": self.ai_metrics,
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "high_severity": sum(1 for v in self.vulnerabilities if v.get("severity") == "High")
            }
        }
        with open(filepath, "w") as f:
            json.dump(report, f, indent=4)
        print(f"[*] JSON report saved to: {filepath}")

    def generate_html(self, filepath="xsstriker/reports/report.html"):
        """Generate a visual report in HTML format (placeholder)."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        html_content = f"<html><body><h1>XSSStriker AI Report</h1><p>Time: {self.report_time}</p></body></html>"
        with open(filepath, "w") as f:
            f.write(html_content)
        print(f"[*] HTML report saved to: {filepath}")

if __name__ == "__main__":
    rg = ReportGenerator([{"url": "http://test.com", "param": "q", "severity": "High"}])
    rg.generate_json("xsstriker/reports/test_report.json")
    rg.generate_html("xsstriker/reports/test_report.html")
