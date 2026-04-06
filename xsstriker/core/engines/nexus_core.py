import asyncio
import sys
import os
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table

# Core Systems
from core.engines.site_oracle import SiteOracle
from core.engines.velocity_fuzz import VelocityFuzz
from core.engines.aura_engine.aura_engine import AuraEngine
from core.engines.strategy_adaptor import StrategyAdaptor
from core.engines.dom_scanner import DOMScanner
from core.rl.haxss_agent import HAXSSAgent
from core.ai.classifier import XSSClassifier
from utils.logger import log_error, log_info
from utils.progress_tracker import ProgressTracker

console = Console()

class NexusCore:
    """System 5: Central Orchestrator & Multi-System Manager (NexusCore)"""
    def __init__(self, target_url):
        self.target_url = target_url
        self.oracle = SiteOracle()
        self.velocity = VelocityFuzz(concurrency=30)
        self.aura = AuraEngine()
        self.strategy = StrategyAdaptor()
        self.dom_scanner = DOMScanner()
        self.haxss = HAXSSAgent()
        self.classifier = XSSClassifier()
        self.tracker = ProgressTracker()
        self.results = []

    async def execute(self, crawl=True, deep_scan=False):
        """Main execution flow: Intelligence -> Fuzzing -> Adaptation -> Verification."""
        console.print(Panel(f"[bold blue]Target:[/bold blue] {self.target_url}", title="NexusCore Initialization"))

        # 1. Intelligence Gathering (SiteOracle)
        with console.status("[bold yellow]System 1: SiteOracle - Gathering Intelligence..."):
             from core.engines.crawler import Crawl4AICrawler
             crawler = Crawl4AICrawler(self.target_url)
             vectors = await crawler.crawl(depth=2)
             for v in vectors:
                 for p in v['params']:
                     self.oracle.save_injection_point(v['url'], p['name'], v['type'])

        all_vectors = self.oracle.get_all_vectors()
        console.print(f"[bold green][+] SiteOracle mapped {len(all_vectors)} potential injection points.[/bold green]")

        # 2. High-Speed Fuzzing (VelocityFuzz)
        payload_probes = ["xsstriker_probe", "d3v_probe", "<u>", "'\">"]
        with console.status("[bold magenta]System 2: VelocityFuzz - High-Speed Fuzzing..."):
             fuzz_results = await self.velocity.fuzz(all_vectors, payload_probes)

        console.print(f"[bold green][+] VelocityFuzz identified {len(fuzz_results)} reflecting parameters.[/bold green]")

        # 3. Targeted AI Verification (AuraEngine + HAXSS + DOMScanner)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            scan_task = progress.add_task("[cyan]System 3 & 4: AI Adaptation & Verification...", total=len(fuzz_results))

            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                for fr in fuzz_results:
                    progress.update(scan_task, description=f"[cyan]Verifying: {fr['url']} | Param: {fr['param']}")

                    # Context Analysis (AuraEngine - xsstrike-equivalent logic)
                    try:
                        # Use actual page content for analysis (AuraEngine expects requests-like response object)
                        import requests
                        # Use a synchronous requests call for AuraEngine compatibility if needed,
                        # but AuraEngine only uses .text and .content usually.
                        # We simulate it with a simple class.
                        class MockResponse:
                            def __init__(self, text):
                                self.text = text

                        resp = await client.get(fr['url'], params={fr['param']: "xssstriker_probe"})
                        occurences = self.aura.analyze_page_context(MockResponse(resp.text))

                        # Determine context based on the deepest occurrence
                        if not occurences:
                            context_type = "html"
                        else:
                            # Context map from AuraEngine (XSStrike)
                            # i[i]['context'] typically 'html', 'attribute', 'script', 'comment'
                            context_type = list(occurences.values())[0]['context']
                            log_info(f"[*] AuraEngine detected context: {context_type} for {fr['url']}")
                    except Exception as e:
                        log_error(f"NexusCore Context Error: {e}")
                        context_type = "html"

                    # Adaptive Loop (StrategyAdaptor + RL)
                    for i in range(10): # Attempts per vulnerable parameter
                        # 1. AI Suggestion (Native XSStrike Payloads + RL Mutation)
                        if i == 0 and occurences:
                             # Try native XSStrike payload first
                             try:
                                 suggested_payloads = self.aura.generate_native_payloads(occurences, resp.text)
                                 # suggested_payloads is a dict {priority: set(payloads)}
                                 # We try priority 10 or the highest available
                                 best_priority = max(suggested_payloads.keys()) if suggested_payloads else 0
                                 if best_priority > 0 and suggested_payloads[best_priority]:
                                     payload = list(suggested_payloads[best_priority])[0]
                                 else:
                                     payload = self.haxss.generate_payload({"type": context_type})
                             except:
                                 payload = self.haxss.generate_payload({"type": context_type})
                        else:
                             payload = self.haxss.generate_payload({"type": context_type})

                        screenshot_path = f"xsstriker/reports/proof_{len(self.results)}_{i}.png"

                        # 2. Verification (DOMScanner - Playwright)
                        xss_triggered = await self.dom_scanner.scan(fr['url'], fr['param'], payload, screenshot_path=screenshot_path)

                        if xss_triggered:
                            self.results.append({
                                "url": fr['url'],
                                "param": fr['param'],
                                "payload": payload,
                                "type": f"Confirmed ({context_type})",
                                "screenshot": screenshot_path
                            })
                            console.print(f"\n[bold red][!] VULNERABILITY CONFIRMED: {fr['url']} (param: {fr['param']})[/bold red]")
                            self.haxss.update(payload, "success", {"type": context_type})
                            break
                        else:
                            # 3. Strategy Adaptation (Self-Correction)
                            if os.path.exists(screenshot_path): os.remove(screenshot_path)

                            # Analyze failure using status code (placeholder for now)
                            status_code = resp.status_code if 'resp' in locals() else None
                            suggested_strategy = self.strategy.analyze_failure(status_code, resp.text if 'resp' in locals() else "", payload)
                            payload = self.strategy.adapt_payload(payload, suggested_strategy, self.haxss.sanitization_agent)

                            self.haxss.update(payload, "failure", {"type": context_type})

                    progress.advance(scan_task)

        # 4. Final Reporting
        self._display_summary()

    def _display_summary(self):
        """Displays the final scan summary table."""
        table = Table(title="NexusCore Scan Summary")
        table.add_column("Target URL", style="cyan")
        table.add_column("Parameter", style="magenta")
        table.add_column("Payload", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Screenshot", style="blue")

        for r in self.results:
            table.add_row(r['url'], r['param'], r['payload'], r['type'], r['screenshot'])

        console.print("\n")
        console.print(table)
        console.print(Panel(f"[bold green][+] NexusCore scan complete! {len(self.results)} vulnerabilities found.[/bold green]", border_style="green"))

if __name__ == "__main__":
    import asyncio
    # nexus = NexusCore("http://example.com")
    # asyncio.run(nexus.execute())
