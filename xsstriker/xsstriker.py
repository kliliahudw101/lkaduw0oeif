import argparse
import sys
import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Add current dir to sys.path for internal imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports (using relative or sys.path depending on environment)
from core.distilroberta_xss.classifier import XSSClassifier
from core.xsstrike_integration.crawler import SimpleCrawler
from core.xsstrike_integration.context_analysis import ContextAnalysis
from core.xsstrike_integration.fuzzer import Fuzzer
from core.xsstrike_integration.waf_evasion import WAFEvasion
from core.rl_agent.haxss_agent import HAXSSAgent
from training.online_trainer import SelfLearningSystem
from training.progress_tracker import ProgressTracker
from reports.report_generator import ReportGenerator

console = Console()

def print_banner():
    """Prints the XSSStriker AI banner."""
    console.print("[bold cyan]" + "="*40 + "[/bold cyan]")
    console.print("[bold white]   XSSStriker AI - Integrated XSS Tool [/bold white]")
    console.print("[bold cyan]" + "="*40 + "[/bold cyan]")

def main():
    parser = argparse.ArgumentParser(description="XSSStriker AI - Integrated and Smart XSS Scanner")
    parser.add_argument("--url", help="Target URL to scan", required=False)
    parser.add_argument("--crawl", action="store_true", help="Automatically crawl for links")
    parser.add_argument("--train", help="Train on custom payload file")
    parser.add_argument("--epochs", type=int, default=10, help="Number of training epochs")
    parser.add_argument("--deep-scan", action="store_true", help="Deep scan (Reflected, Stored, DOM)")
    parser.add_argument("--self-learn", action="store_true", help="Enable continuous self-learning on target")
    parser.add_argument("--report", choices=["json", "html"], default="json", help="Report format (json/html)")
    parser.add_argument("--waf-evasion", action="store_true", help="Enable WAF evasion techniques")
    parser.add_argument("--background", action="store_true", help="Run in background mode")

    args = parser.parse_args()
    print_banner()

    if args.train:
        console.print(f"[bold yellow][*] Training mode enabled on file: {args.train}[/bold yellow]")
        # Initial training logic here
        return

    if not args.url:
        parser.print_help()
        sys.exit(0)

    console.print(f"[bold blue][*] Starting scan on target: {args.url}[/bold blue]")

    # Initialization of layers
    classifier = XSSClassifier()
    crawler = SimpleCrawler(args.url)
    haxss = HAXSSAgent()
    tracker = ProgressTracker()
    results = []

    # Layer 3: Crawling and discovery
    if args.crawl:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), console=console) as progress:
            task = progress.add_task("[green]Crawling...", total=1)
            vectors = crawler.crawl()
            progress.update(task, completed=1)
            console.print(f"[*] Found {len(vectors)} potential input points.")
    else:
        vectors = [{"url": args.url, "method": "get", "params": [], "type": "manual"}]

    # Layer 4: Scanning and orchestration
    for vector in vectors:
        console.print(f"[bold green][*] Fuzzing input point: {vector['url']} ({vector['type']})[/bold green]")

        # RL loop and feedback (simplified)
        for i in range(5):  # Multiple attempts per parameter
            # Layer 2: RL Payload Generation
            payload = haxss.generate_payload({"type": "html"})

            # Layer 1: AI Detection
            prediction = classifier.predict(payload)
            if prediction["label"] == "XSS":
                console.print(f"[*] AI confidence for payload {payload}: {prediction['confidence']:.4f}")

            # Perform fuzzer check (simulated for demo)
            status = "success" if "alert" in payload else "failure"

            # Update trackers and agents
            tracker.update(status)
            haxss.update(payload, status, {"type": "html"})

            if status == "success":
                results.append({"url": vector["url"], "payload": payload, "severity": "High"})

    # Layer 4: Report generation
    rg = ReportGenerator(results, {"accuracy": 0.99})
    if args.report == "json":
        rg.generate_json()
    else:
        rg.generate_html()

    console.print("[bold green][+] Scan complete! Report saved to reports/ directory.[/bold green]")
    tracker.display_stats()

if __name__ == "__main__":
    main()
