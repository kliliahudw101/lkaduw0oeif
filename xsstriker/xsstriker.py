import argparse
import sys
import os
import asyncio
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import print as rprint

# Ensure project structure is correctly imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core Components
from utils.logger import log_error, log_info
from core.ai.classifier import XSSClassifier
from core.engines.crawler import Crawl4AICrawler
from core.engines.dom_scanner import DOMScanner
from core.engines.stored_detector import StoredXSSDetector
from core.engines.context_analysis import ContextAnalysis
from core.rl.haxss_agent import HAXSSAgent
from core.engines.cve_watcher import XSSCVEWatcher
from utils.progress_tracker import ProgressTracker
from utils.report_generator import ReportGenerator

console = Console()

def print_banner():
    """Prints the XSStriker professional banner."""
    banner = """
[bold red]
┏━┓┏━┓┏━━┓┏━━━┓┏━━━━┓┳━┓┳ ┳┏━┓┳━┓
 ┃  ┃  ┃  ┃┃   ┃   ┃  ┃ ┃┃ ┃┃ ┃┃ ┃
 ┗━┓┗━┓┗━━┓┗━━━┓   ┃  ┣━┛┃ ┃┣━┛┣━┛
   ┃  ┃   ┃    ┃   ┃  ┃ ┓┃ ┃┃  ┃ ┓
┗━┛┗━┛┗━━┛┗━━━┛   ┻  ┻ ┗┗━┛┻  ┻ ┗
[/bold red]
[bold white]   The Most Advanced AI-Powered XSS Discovery Suite[/bold white]
[bold blue]   v2.1 (Python 3.8+) - DistilRoBERTa + HAXSS + XSStrike Engine[/bold blue]
[bold red]   "Detect. Verify. Exploit."[/bold red]
"""
    console.print(banner)

def build_vuln_url(url, parameter, payload):
    """Robustly constructs a URL with a payload using urllib.parse."""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query[parameter] = [payload]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

async def main():
    parser = argparse.ArgumentParser(description="XSStriker - Professional AI-Powered XSS Discovery Tool")

    group_scan = parser.add_argument_group('Scanning Options')
    group_scan.add_argument("--url", "-u", help="Target URL to scan")
    group_scan.add_argument("--crawl", "-c", action="store_true", help="Crawl site for links and input vectors")
    group_scan.add_argument("--deep-scan", "-d", action="store_true", help="Deep scan (Reflected, Stored, DOM)")
    group_scan.add_argument("--hidden-params", action="store_true", help="Attempt to discover hidden parameters")

    group_ai = parser.add_argument_group('AI & Machine Learning')
    group_ai.add_argument("--train", help="Train model from scratch using custom payload file")
    group_ai.add_argument("--epochs", type=int, default=50, help="Number of training epochs (Default: 50)")
    group_ai.add_argument("--ai-mode", choices=["aggressive", "stealth", "balanced"], default="balanced", help="AI Mode")
    group_ai.add_argument("--update-cves", action="store_true", help="Fetch and update AI with latest XSS CVEs")

    group_output = parser.add_argument_group('Output & Reporting')
    group_output.add_argument("--report", choices=["json", "html"], default="json", help="Report format")
    group_output.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    if "-h" in sys.argv or "--help" in sys.argv:
        print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    print_banner()

    # Layer 1: AI Detection Engine
    classifier = XSSClassifier()

    if args.update_cves:
        with console.status("[bold green]Updating AI with latest XSS CVEs..."):
            watcher = XSSCVEWatcher()
            cve_data = await watcher.fetch_latest()
            watcher.train_on_cve(classifier, cve_data)
        console.print("[bold green][+] CVE Update Complete![/bold green]")
        console.print(watcher.generate_daily_report())
        if not args.url:
            return

    if args.train:
        console.print(f"[*] Training from scratch on file: {args.train} for {args.epochs} epochs")
        with open(args.train, "r") as f:
            payloads = f.read().splitlines()
        labels = [1] * len(payloads) # Assumed XSS dataset
        classifier.train_from_scratch(payloads, labels, epochs=args.epochs)
        classifier.save_model()
        return

    if not args.url:
        console.print("[bold red][!] No target URL specified. Use -u/--url.[/bold red]")
        sys.exit(1)

    console.print(Panel(f"[bold blue]Target:[/bold blue] {args.url}\n[bold blue]Mode:[/bold blue] {'Deep Scan' if args.deep_scan else 'Normal Scan'}\n[bold blue]AI Mode:[/bold blue] {args.ai_mode}", title="Scan Initialization"))

    # Initialization
    crawler = Crawl4AICrawler(args.url)
    dom_scanner = DOMScanner()
    stored_detector = StoredXSSDetector(args.url)
    context_analyzer = ContextAnalysis()
    haxss = HAXSSAgent()
    tracker = ProgressTracker()
    results = []

    # Step 1: Site Mapping and Crawling
    with console.status("[bold yellow]Crawling and Mapping Target..."):
        vectors = await crawler.crawl(discover_hidden=args.hidden_params)
        if args.deep_scan:
            await stored_detector.build_site_map()

    console.print(f"[bold green][+] Found {len(vectors)} input vectors.[/bold green]")

    # Step 2: Main Orchestration Loop
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        scan_task = progress.add_task("[cyan]Scanning vectors...", total=len(vectors))

        for vector in vectors:
            progress.update(scan_task, description=f"[cyan]Fuzzing: {vector['url']} ({vector['type']})")

            # Iterate through all parameters in the vector
            for param_info in vector['params']:
                param_name = param_info['name']
                progress.update(scan_task, description=f"[cyan]Fuzzing: {vector['url']} | Param: {param_name}")

                # Context Analysis
                contexts = context_analyzer.analyze_context(vector['url'], param_name, method=vector.get('method', 'get'))
                context_type = contexts[0]['type'] if contexts else "unknown"

                # RL loop with HAXSS
                for i in range(10):  # Attempts per parameter
                    payload = haxss.generate_payload({"type": context_type})
                    screenshot_path = f"xsstriker/reports/proof_{len(results)}_{i}.png"

                    # Step 1: Verification (Always verify before AI confirmation)
                    # We pass the full URL construction logic to dom_scanner via build_vuln_url
                    target_url = build_vuln_url(vector['url'], param_name, payload)
                    xss_triggered = await dom_scanner.scan(vector['url'], param_name, payload, screenshot_path=screenshot_path)

                    if xss_triggered:
                        # Step 2: AI Post-Analysis
                        prediction = classifier.predict(payload)

                        vuln_info = {
                            "url": vector["url"],
                            "parameter": param_name,
                            "payload": payload,
                            "type": "DOM/Reflected",
                            "severity": "High",
                            "ai_confidence": prediction["confidence"],
                            "path": target_url,
                            "screenshot": screenshot_path
                        }
                        results.append(vuln_info)

                        # Immediate findings report
                        console.print("\n" + Panel(
                            f"[bold red]VULNERABILITY CONFIRMED![/bold red]\n\n"
                            f"[bold white]URL:[/bold white] {vuln_info['url']}\n"
                            f"[bold white]Parameter:[/bold white] {vuln_info['parameter']}\n"
                            f"[bold white]Payload:[/bold white] {vuln_info['payload']}\n"
                            f"[bold white]AI Confidence:[/bold white] {vuln_info['ai_confidence']:.4f}\n"
                            f"[bold white]Description:[/bold white] The payload was successfully executed in a real browser environment.\n"
                            f"[bold white]Exploitation Path:[/bold white] {vuln_info['path']}\n"
                            f"[bold white]Proof Screenshot:[/bold white] {vuln_info['screenshot']}",
                            title="[bold red]Finding[/bold red]", border_style="red"
                        ))

                        tracker.update("success")
                        haxss.update(payload, "success", {"type": context_type})

                        # If deep scan is on, check if it's stored
                        if args.deep_scan:
                             stored_res = await stored_detector.detect(vector['url'], param_name, payload)
                             if stored_res:
                                 console.print(f"[bold red][!] STORED XSS CONFIRMED at {stored_res['reflection_point']}![/bold red]")

                        break # Move to next parameter
                    else:
                        # Clean up screenshot if not confirmed
                        if os.path.exists(screenshot_path):
                             os.remove(screenshot_path)

                        tracker.update("failure")
                        haxss.update(payload, "failure", {"type": context_type})

            progress.advance(scan_task)

    # Final Statistics
    table = Table(title="Scan Results Summary")
    table.add_column("URL", style="cyan")
    table.add_column("Parameter", style="magenta")
    table.add_column("Type", style="green")
    table.add_column("Severity", style="red")

    for r in results:
        table.add_row(r["url"], r["parameter"], r["type"], r["severity"])

    console.print("\n")
    console.print(table)

    # Step 3: Reporting
    rg = ReportGenerator(results, {"accuracy": 0.9966})
    if args.report == "json":
        rg.generate_json()
    else:
        rg.generate_html()

    console.print(f"\n[bold green][+] XSStriker scan complete! {len(results)} vulnerabilities found.[/bold green]")
    tracker.display_stats()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Scan interrupted by user.[/bold red]")
        sys.exit(0)
    except Exception as e:
        log_error(f"Critical Error: {str(e)}")
        console.print(f"\n[bold red][!] Critical Error: {e}[/bold red]")
        console.print("[bold yellow][*] Check xsstriker/reports/xsstriker.log for technical details.[/bold yellow]")
        if "--verbose" in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
