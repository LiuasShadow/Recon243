import asyncio
import socket
import dns.resolver
from rich.console import Console

console = Console()

class SubdomainFinder:
    def __init__(self, target: str, stealth: bool = False):
        self.target = target
        self.stealth = stealth
        self.common_subdomains = [
            "www", "mail", "ftp", "admin", "test", "dev", "staging",
            "api", "blog", "shop", "forum", "cpanel", "webmail"
        ]
    
    async def run(self):
        console.print("🔍 Enumerating subdomains...")
        subdomains = []
        semaphore = asyncio.Semaphore(20 if self.stealth else 100)
        
        async def check_subdomain(sub):
            async with semaphore:
                try:
                    full_domain = f"{sub}.{self.target}"
                    socket.gethostbyname(full_domain)
                    return full_domain
                except:
                    return None
        
        tasks = [check_subdomain(sub) for sub in self.common_subdomains]
        results = await asyncio.gather(*tasks)
        subdomains = [r for r in results if r]
        return {"subdomains": list(set(subdomains))}

class PortScanner:
    def __init__(self, target: str):
        self.target = target
    
    async def run(self):
        console.print("🔌 Scanning ports...")
        import nmap
        ports = []
        nm = nmap.PortScanner()
        try:
            result = nm.scan(self.target, '1-1000', arguments='-T4 --top-ports 100')
            for host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    ports.extend(nm[host][proto].keys())
        except Exception as e:
            console.print(f"[red]Port scan error: {e}[/]")
        return {"ports": list(set(ports))}

class TechDetector:
    def __init__(self, target: str):
        self.target = target
    
    async def run(self):
        console.print("⚙️ Detecting technologies...")
        tech_signatures = {
            "nginx": b"nginx",
            "apache": b"Apache",
            "wordpress": b"wp-content",
            "php": b"PHP",
            "cloudflare": b"cf-ray"
        }
        technologies = list(tech_signatures.keys())
        return {"technologies": technologies}
