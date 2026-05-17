import asyncio
from datetime import datetime
from rich.console import Console
from rich.table import Table
from recon243.recon.modules import SubdomainFinder, PortScanner, TechDetector
from recon243.crawler.crawler import WebCrawler
from recon243.scanner.nikto import NiktoScanner
from recon243.scanner.nuclei import NucleiScanner

console = Console()

class ReconEngine:
    def __init__(self, target: str, threads: int = 50, stealth: bool = False, 
                 recursive: bool = False, verbose: bool = False):
        self.target = target
        self.threads = threads
        self.stealth = stealth
        self.recursive = recursive
        self.verbose = verbose
        self.timestamp = datetime.now().isoformat()
        self.modules = {}
        
    async def run_reconnaissance(self):
        tasks = [
            SubdomainFinder(self.target, stealth=self.stealth).run(),
            PortScanner(self.target).run(),
            TechDetector(self.target).run()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            "subdomains": results[0].get("subdomains", []) if isinstance(results[0], dict) else [],
            "ports": results[1].get("ports", []) if isinstance(results[1], dict) else [],
            "technologies": results[2].get("technologies", []) if isinstance(results[2], dict) else [],
        }
    
    async def run_crawler(self):
        crawler = WebCrawler(
            self.target, 
            recursive=self.recursive,
            stealth=self.stealth,
            threads=self.threads
        )
        return await crawler.crawl()
    
    async def run_vuln_scan(self):
        tasks = [
            NiktoScanner(self.target, stealth=self.stealth).scan(),
            NucleiScanner(self.target).scan()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            "nikto": results[0].get("nikto", []) if isinstance(results[0], dict) else [],
            "nuclei": results[1].get("nuclei", []) if isinstance(results[1], dict) else [],
        }
    
    def print_summary(self, report_data):
        table = Table(title="🎯 RECON243 SUMMARY", show_header=True)
        table.add_column("Category", style="cyan")
        table.add_column("Findings", style="green")
        
        table.add_row("🔍 Subdomains", str(len(report_data['recon']["subdomains"])))
        table.add_row("🔌 Open Ports", str(len(report_data['recon']["ports"])))
        table.add_row("⚙️ Technologies", str(len(report_data['recon']["technologies"])))
        table.add_row("🕷️ Endpoints", str(len(report_data['crawl'].get("urls", []))))
        vulns_count = len(report_data["vulns"].get("nikto", [])) + len(report_data["vulns"].get("nuclei", []))
        table.add_row("🚨 Vulnerabilities", str(vulns_count))
        
        console.print(table)
