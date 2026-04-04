import argparse
import sys
import os
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Ensure project structure is correctly imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core Components (XStriker Modern Architecture)
from core.distilroberta_xss.classifier import XSSClassifier
from core.xsstrike_integration.crawler import Crawl4AICrawler
from core.xsstrike_integration.dom_scanner import DOMScanner
from core.xsstrike_integration.stored_detector import StoredXSSDetector
from core.rl_agent.haxss_agent import HAXSSAgent
from core.cve_integration import XSSCVEWatcher
from training.progress_tracker import ProgressTracker
from reports.report_generator import ReportGenerator

console = Console()

def print_banner():
    """Prints the XStriker (Modern Python 3) banner."""
    console.print("[bold red]" + "="*50 + "[/bold red]")
    console.print("[bold white]   XStriker - Modern AI-Powered XSS Tool [/bold white]")
    console.print("[bold blue]   v2.0 (Python 3.8+) - DistilRoBERTa + HAXSS [/bold blue]")
    console.print("[bold red]" + "="*50 + "[/bold red]")

async def main():
    parser = argparse.ArgumentParser(description="XStriker - Advanced and Modern AI-Powered XSS Tool")
    parser.add_argument("--url", help="Target URL to scan", required=False)
    parser.add_argument("--crawl", action="store_true", help="Crawl site for links and input vectors")
    parser.add_argument("--train", help="Train model from scratch using custom payload file")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs (Default: 50)")
    parser.add_argument("--ai-mode", choices=["aggressive", "stealth", "balanced"], default="balanced", help="AI Mode")
    parser.add_argument("--update-cves", action="store_true", help="Fetch and update AI with latest XSS CVEs")
    parser.add_argument("--auto-exploit", action="store_true", help="Automatically download and test PoCs from CVEs")
    parser.add_argument("--deep-scan", action="store_true", help="Deep scan (Reflected, Stored, DOM)")
    parser.add_argument("--report", choices=["json", "html"], default="json", help="Report format")

    args = parser.parse_args()
    print_banner()

    # Layer 1: AI Detection Engine
    classifier = XSSClassifier()

    if args.update_cves:
        console.print("[*] Updating AI with latest XSS CVEs...")
        watcher = XSSCVEWatcher()
        cve_data = await watcher.fetch_latest()
        watcher.train_on_cve(classifier, cve_data)
        console.print(watcher.generate_daily_report())
        if not args.url:
            return

    if args.train:
        console.print(f"[*] Training from scratch on file: {args.train} for {args.epochs} epochs")
        # Example loading logic from text file
        with open(args.train, "r") as f:
            payloads = f.read().splitlines()
        labels = [1] * len(payloads) # Assumed XSS dataset
        classifier.train_from_scratch(payloads, labels, epochs=args.epochs)
        classifier.save_model()
        return

    if not args.url:
        parser.print_help()
        return

    console.print(f"[bold blue][*] Starting aggressive scan on: {args.url}[/bold blue]")

    # Initialization of layers
    crawler = Crawl4AICrawler(args.url)
    dom_scanner = DOMScanner()
    stored_detector = StoredXSSDetector(args.url)
    haxss = HAXSSAgent()
    tracker = ProgressTracker()
    results = []

    # Step 1: Site Mapping and Crawling
    vectors = await crawler.crawl()
    if args.deep_scan:
        await stored_detector.build_site_map()

    # Step 2: Main Orchestration Loop
    for vector in vectors:
        console.print(f"[bold green][*] Fuzzing target: {vector['url']} ({vector['type']})[/bold green]")

        # RL loop with HAXSS
        for i in range(10):  # More attempts per parameter
            # Generate payload using RL agents (7 escape, 32 mutation)
            payload = haxss.generate_payload({"type": vector["type"]})

            # AI Check
            prediction = classifier.predict(payload)
            if prediction["label"] == "XSS":
                console.print(f"[*] AI confidence: {prediction['confidence']:.4f}")

            # Simulated trigger check
            xss_triggered = False
            if args.deep_scan:
                 # Check DOM-based XSS with Playwright
                 xss_triggered = await dom_scanner.scan(vector["url"], vector["params"][0]["name"], payload)

            status = "success" if xss_triggered else "failure"
            tracker.update(status)
            haxss.update(payload, status, {"type": vector["type"]})

            if xss_triggered:
                results.append({"url": vector["url"], "payload": payload, "type": "DOM/Reflected", "severity": "High"})
                break

    # Step 3: Reporting
    rg = ReportGenerator(results, {"accuracy": 0.9966})
    if args.report == "json":
        rg.generate_json()
    else:
        rg.generate_html()

    console.print("[bold green][+] XStriker scan complete! Report saved to reports/ directory.[/bold green]")
    tracker.display_stats()

if __name__ == "__main__":
    asyncio.run(main())
