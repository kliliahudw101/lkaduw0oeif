import argparse
import sys
import os
import asyncio
from rich.console import Console

# Ensure project structure is correctly imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core Systems
from core.engines.nexus_core import NexusCore
from core.engines.cve_watcher import XSSCVEWatcher
from core.ai.classifier import XSSClassifier
from utils.logger import log_error, log_info

console = Console()

def print_banner():
    """Prints the XSStriker System of Systems banner."""
    banner = """
[bold red]
┏━┓┏━┓┏━━┓┏━━━┓┏━━━━┓┳━┓┳ ┳┏━┓┳━┓
 ┃  ┃  ┃  ┃┃   ┃   ┃  ┃ ┃┃ ┃┃ ┃┃ ┃
 ┗━┓┗━┓┗━━┓┗━━━┓   ┃  ┣━┛┃ ┃┣━┛┣━┛
   ┃  ┃   ┃    ┃   ┃  ┃ ┓┃ ┃┃  ┃ ┓
┗━┛┗━┛┗━━┛┗━━━┛   ┻  ┻ ┗┗━┛┻  ┻ ┗
[/bold red]
[bold white]   The Most Advanced AI-Powered Multi-System Suite (NexusCore)[/bold white]
[bold blue]   v2.5 (Python 3.8+) - Intelligence. Speed. Adaptation. Verification.[/bold blue]
[bold red]   "System 1: SiteOracle | System 2: VelocityFuzz | System 3: AuraEngine"[/bold red]
"""
    console.print(banner)

async def main():
    parser = argparse.ArgumentParser(description="XSStriker NexusCore - Multi-System AI-Powered Discovery Tool")

    group_scan = parser.add_argument_group('NexusCore Scanning Options')
    group_scan.add_argument("--url", "-u", help="Target URL to scan")
    group_scan.add_argument("--crawl", "-c", action="store_true", help="System 1: SiteOracle - Map Site")
    group_scan.add_argument("--deep-scan", "-d", action="store_true", help="System 1: SiteOracle - Deep Scan")
    group_scan.add_argument("--hidden-params", action="store_true", help="System 1: SiteOracle - Discover Hidden Parameters")

    group_ai = parser.add_argument_group('AuraEngine & ML')
    group_ai.add_argument("--train", help="Train AI from scratch using custom payload file")
    group_ai.add_argument("--epochs", type=int, default=50, help="Number of training epochs (Default: 50)")
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

    if args.update_cves:
        with console.status("[bold green]Updating AI with latest XSS CVEs..."):
            watcher = XSSCVEWatcher()
            cve_data = await watcher.fetch_latest()
            classifier = XSSClassifier()
            watcher.train_on_cve(classifier, cve_data)
        console.print("[bold green][+] CVE Update Complete![/bold green]")
        console.print(watcher.generate_daily_report())
        if not args.url:
            return

    if args.train:
        console.print(f"[*] Training from scratch on file: {args.train} for {args.epochs} epochs")
        classifier = XSSClassifier()
        with open(args.train, "r") as f:
            payloads = f.read().splitlines()
        labels = [1] * len(payloads) # Assumed XSS dataset
        classifier.train_from_scratch(payloads, labels, epochs=args.epochs)
        classifier.save_model()
        return

    if not args.url:
        console.print("[bold red][!] No target URL specified. Use -u/--url.[/bold red]")
        sys.exit(1)

    # Launch NexusCore Execution Flow
    nexus = NexusCore(args.url)
    await nexus.execute(crawl=args.crawl, deep_scan=args.deep_scan)

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
