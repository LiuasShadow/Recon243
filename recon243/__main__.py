#!/usr/bin/env python3
import argparse
import asyncio
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from recon243.core.engine import ReconEngine
from recon243.report.generator import HTMLReportGenerator

console = Console()

def parse_args():
    parser = argparse.ArgumentParser(description="Recon243 - Automated Recon & Vuln Scanner")
    parser.add_argument("-t", "--target", required=True, help="Target domain/IP/URL")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-s", "--stealth", action="store_true", help="Stealth mode")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive crawling")
    parser.add_argument("--html", help="Generate HTML report")
    parser.add_argument("--threads", type=int, default=50, help="Thread count")
    return parser.parse_args()

async def main():
    args = parse_args()
    
    console.print("""
[bold cyan]╔══════════════════════════════════════════════════════╗[/]
[bold cyan]║[/] [bold yellow]Recon243[/] [dim]- Automated Reconnaissance & Vuln Scanner[/] [bold cyan]║[/]
[bold cyan]║[/] [dim]Author: Liuas25 | v1.0.0 | Ethical Hacking Only[/] [bold cyan]║[/]
[bold cyan]╚══════════════════════════════════════════════════════╝[/]
    """)
    
    console.print(f"[bold green]🎯 Target:[/] [yellow]{args.target}[/]")
    console.print(f"[bold green]⚙️ Mode:[/] {'🛡️ Stealth' if args.stealth else '🚀 Full Speed'}")
    
    engine = ReconEngine(
        target=args.target,
        threads=args.threads,
        stealth=args.stealth,
        recursive=args.recursive,
        verbose=args.verbose
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        recon_task = progress.add_task("🔍 Reconnaissance...", total=None)
        recon_data = await engine.run_reconnaissance()
        progress.remove_task(recon_task)
        
        crawl_task = progress.add_task("🕷️ Crawling...", total=None)
        crawl_data = await engine.run_crawler()
        progress.remove_task(crawl_task)
        
        vuln_task = progress.add_task("🛡️ Vulnerability Scan...", total=None)
        vuln_data = await engine.run_vuln_scan()
        progress.remove_task(vuln_task)
    
    console.print("\n" + "="*80)
    console.print("[bold green]📊 RECON243 SCAN COMPLETE[/]")
    console.print("="*80)
    
    report_data = {
        "target": args.target,
        "recon": recon_data,
        "crawl": crawl_data,
        "vulns": vuln_data,
        "timestamp": engine.timestamp
    }
    
    engine.print_summary(report_data)
    
    if args.html:
        generator = HTMLReportGenerator(report_data)
        generator.generate(args.html)
        console.print(f"[bold green]✨ HTML Report:[/] [yellow]{args.html}[/]")

if __name__ == "__main__":
    asyncio.run(main())
