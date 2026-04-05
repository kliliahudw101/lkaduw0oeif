import httpx
from bs4 import BeautifulSoup
import re
import os
import datetime

class XSSCVEWatcher:
    """Layer 4: CVE Integration (Fetch and fetch XSS-specific CVEs)"""
    def __init__(self, sources=None):
        self.sources = sources if sources else [
            "https://cve.mitre.org/cgi-bin/cvekey.cgi?keyword=xss",
            "https://nvd.nist.gov/vuln/search/results?form_type=Basic&results_type=overview&search_type=all&isCpeNameSearch=false&query=xss",
            "https://packetstormsecurity.com/files/tags/xss/",
            "https://www.exploit-db.com/?platform=webapps&order_by=date&order=desc&search=xss"
        ]
        self.cve_data = []

    async def fetch_latest(self, limit=100):
        """Fetch latest XSS CVEs from sources."""
        print(f"[*] Fetching latest XSS CVEs (limit: {limit})...")

        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            # Mitigation source scrape (Example Mitre)
            try:
                response = await client.get(self.sources[0])
                soup = BeautifulSoup(response.text, "html.parser")

                # Simple extraction: Find CVE IDs and descriptions
                cve_table = soup.find("div", {"id": "TableStyle"})
                if cve_table:
                    for row in cve_table.find_all("tr")[1:limit+1]:
                        cols = row.find_all("td")
                        if len(cols) >= 2:
                            cve_id = cols[0].text.strip()
                            description = cols[1].text.strip()
                            self.cve_data.append({
                                "id": cve_id,
                                "description": description,
                                "date": datetime.date.today().isoformat(),
                                "severity": self.infer_severity(description)
                            })

                print(f"[+] Found {len(self.cve_data)} XSS CVEs.")
                return self.cve_data

            except Exception as e:
                print(f"[!] CVE Fetch error: {e}")
                return []

    def infer_severity(self, description):
        """Heuristic severity estimation based on description keywords."""
        description = description.lower()
        if "critical" in description or "unauthenticated" in description or "rce" in description:
            return "Critical"
        if "high" in description or "administrative" in description or "admin" in description:
            return "High"
        if "medium" in description or "stored" in description:
            return "Medium"
        return "Low"

    async def download_poc(self, cve_id):
        """Placeholder for downloading PoC from exploit-db or PacketStorm."""
        print(f"[*] Attempting to download PoC for {cve_id}...")
        # In a real tool, search exploit-db for cve_id and download the script
        poc_content = f"XSS PoC for {cve_id} simulated content."
        os.makedirs("data/cve_pocs", exist_ok=True)
        with open(f"data/cve_pocs/{cve_id}_poc.txt", "w") as f:
            f.write(poc_content)
        return poc_content

    def train_on_cve(self, classifier, cve_data):
        """Train AI on new exploit descriptions or PoC strings."""
        print(f"[*] Training AI on new CVE data ({len(cve_data)} entries)...")
        texts = [d["description"] for d in cve_data]
        labels = [1] * len(texts) # All CVEs are XSS (1)
        # Call training from Layer 1
        classifier.train_from_scratch(texts, labels, epochs=2)
        print("[+] AI updated with latest CVE knowledge.")

    def generate_daily_report(self):
        """Technical report on new CVEs (2026-04-03 format)."""
        date_str = datetime.date.today().isoformat()
        total = len(self.cve_data)
        critical = sum(1 for c in self.cve_data if c["severity"] == "Critical")
        high = sum(1 for c in self.cve_data if c["severity"] == "High")

        report = f"\n📊 XSS CVE Daily Report ({date_str})\n"
        report += "=" * 40 + "\n"
        report += f"New CVEs: {total}\n"
        report += f"Critical: {critical}\n"
        report += f"High: {high}\n"
        report += f"Medium: {total - critical - high}\n\n"
        report += "Top CVEs:\n"
        for cve in self.cve_data[:5]:
            report += f"- {cve['id']}: {cve['description'][:60]}... ({cve['severity']})\n"

        return report

if __name__ == "__main__":
    import asyncio
    watcher = XSSCVEWatcher()
    # asyncio.run(watcher.fetch_latest())
    # print(watcher.generate_daily_report())
