"""
Distributed A2A Client - Orchestrates calls across multiple A2A services.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .servers.auth import A2AAuth


class DistributedA2AClient:
    """Client for orchestrating distributed A2A research workflows."""
    
    def __init__(self, registry_url: str = "http://127.0.0.1:8000", shared_secret: str = "demo-secret"):
        self.registry_url = registry_url
        self.shared_secret = shared_secret
        self.auth = A2AAuth(shared_secret)
        self.console = Console()
        self.client_name = "research-client"
        
        # Service URLs (discovered from registry)
        self.services = {}
    
    async def discover_services(self):
        """Discover services from the registry."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.registry_url}/services")
                if response.status_code == 200:
                    services = response.json()
                    print(f"[client] Found {len(services)} registered services")
                    
                    for service in services:
                        status = service['status']
                        service_name = service['service_name']
                        service_url = service['url']
                        
                        print(f"[client] Service {service_name}: {status} at {service_url}")
                        
                        if status in ['healthy', 'unknown', 'unhealthy']:
                            # Accept all services for now (registry health check might be flaky)
                            self.services[service_name] = service_url
                            if status != 'healthy':
                                print(f"[client] Accepting service {service_name} with status: {status}")
                    
                    print(f"[client] Discovered {len(self.services)} available services")
                    return len(self.services) > 0
                else:
                    print(f"[client] Failed to discover services: {response.status_code}")
                    return False
        except Exception as e:
            print(f"[client] Service discovery error: {e}")
            return False
    
    async def perform_distributed_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform distributed web search."""
        if "web-search" not in self.services:
            raise Exception("Web search service not available")
        
        search_url = f"{self.services['web-search']}/search"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {
            "query_text": query,
            "max_results": max_results,
            "comprehensive": True  # Enable comprehensive multi-round search
        }
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Searching: [bold]{query}[/bold]", total=None)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    search_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['results']
                else:
                    raise Exception(f"Search failed: {response.status_code} - {response.text}")
    
    async def extract_insights(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from search results."""
        if "knowledge-extraction" not in self.services:
            raise Exception("Knowledge extraction service not available")
        
        extract_url = f"{self.services['knowledge-extraction']}/extract"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {"search_results": search_results}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Extracting insights...", total=None)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    extract_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise Exception(f"Insight extraction failed: {response.status_code} - {response.text}")
    
    async def analyze_credibility(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze source credibility."""
        if "knowledge-extraction" not in self.services:
            raise Exception("Knowledge extraction service not available")
        
        credibility_url = f"{self.services['knowledge-extraction']}/credibility"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {"search_results": search_results}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                credibility_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Credibility analysis failed: {response.status_code} - {response.text}")
    
    async def start_research_session(self, topic: str) -> str:
        """Start a new research session."""
        if "research-aggregation" not in self.services:
            raise Exception("Research aggregation service not available")
        
        session_url = f"{self.services['research-aggregation']}/session"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {"topic": topic}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                session_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['session_id']
            else:
                raise Exception(f"Session creation failed: {response.status_code} - {response.text}")
    
    async def aggregate_results(self, session_id: str, results: List[Dict[str, Any]]):
        """Aggregate results for a research session."""
        if "research-aggregation" not in self.services:
            raise Exception("Research aggregation service not available")
        
        aggregate_url = f"{self.services['research-aggregation']}/aggregate"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {
            "session_id": session_id,
            "results": results
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                aggregate_url,
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Result aggregation failed: {response.status_code} - {response.text}")
    
    async def generate_report(self, session_id: str) -> Dict[str, Any]:
        """Generate research report."""
        if "research-aggregation" not in self.services:
            raise Exception("Research aggregation service not available")
        
        report_url = f"{self.services['research-aggregation']}/report"
        headers = self.auth.create_auth_headers(self.client_name, "")
        
        payload = {"session_id": session_id}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Generating report...", total=None)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    report_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['report']
                else:
                    raise Exception(f"Report generation failed: {response.status_code} - {response.text}")
    
    def display_search_results(self, query: str, results: List[Dict[str, Any]]):
        """Display search results in a formatted table."""
        if not results:
            self.console.print("[red]No results found.[/red]")
            return
        
        self.console.print(f"\n[bold green]Search Results for:[/bold green] [bold]{query}[/bold]")
        self.console.print()
        
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Title", style="bold", max_width=40)
        table.add_column("Source", style="dim", max_width=20)
        table.add_column("Snippet", max_width=50)
        table.add_column("Relevance", justify="center", max_width=10)
        
        for result in results:
            relevance = f"{result.get('relevance_score', 0.8):.1f}"
            snippet = result.get('snippet', '')
            if len(snippet) > 100:
                snippet = snippet[:100] + "..."
                
            table.add_row(
                result.get('title', 'No title'),
                result.get('source', 'Unknown'),
                snippet,
                relevance
            )
        
        self.console.print(table)
        self.console.print()
    
    def display_insights(self, insights_data: Dict[str, Any]):
        """Display extracted insights."""
        insights = insights_data.get('insights', [])
        
        if not insights:
            self.console.print("[yellow]No insights extracted.[/yellow]")
            return
        
        self.console.print(f"[bold green]✓[/bold green] Extracted {len(insights)} insights")
        
        for insight in insights[:3]:  # Show first 3 insights
            self.console.print(f"  • {insight['content']} ([dim]{insight['insight_type']}[/dim])")
    
    def display_credibility(self, credibility_data: Dict[str, Any]):
        """Display credibility analysis."""
        analysis = credibility_data.get('analysis', {})
        
        high_cred = analysis.get('high_credibility_count', 0)
        total = analysis.get('total_sources', 0)
        
        if total > 0:
            percentage = (high_cred / total) * 100
            self.console.print(f"[bold green]✓[/bold green] Source credibility: {high_cred}/{total} high-credibility sources ({percentage:.1f}%)")
    
    def display_report(self, report: Dict[str, Any]):
        """Display comprehensive research report."""
        # Basic statistics
        stats_content = (
            f"[bold]Research Statistics[/bold]\n"
            f"• Topic: [bold]{report.get('topic', 'Unknown')}[/bold]\n"
            f"• Sources analyzed: [bold]{report.get('total_sources', 0)}[/bold]\n"
            f"• Unique domains: [bold]{report.get('unique_domains', 0)}[/bold]\n"
            f"• Total insights: [bold]{report.get('total_insights', 0)}[/bold]\n"
            f"• Average relevance: [bold]{report.get('average_relevance', 0):.2f}[/bold]\n"
            f"• Session duration: [bold]{report.get('session_duration', 'Unknown')}[/bold]\n\n"
            f"[dim]Session ID: {report.get('session_id', 'Unknown')}[/dim]"
        )
        
        stats_panel = Panel(stats_content, title="📊 Research Statistics", border_style="blue")
        self.console.print(stats_panel)
        self.console.print()
        
        # Executive Summary
        if report.get('executive_summary'):
            summary_panel = Panel(
                report['executive_summary'],
                title="📋 Executive Summary",
                border_style="green"
            )
            self.console.print(summary_panel)
            self.console.print()
        
        # Key Findings
        if report.get('key_findings'):
            findings_content = "\n".join([f"• {finding}" for finding in report['key_findings']])
            findings_panel = Panel(
                findings_content,
                title="🔍 Key Findings",
                border_style="yellow"
            )
            self.console.print(findings_panel)
            self.console.print()
        
        # Detailed Analysis
        if report.get('detailed_analysis'):
            analysis_panel = Panel(
                report['detailed_analysis'],
                title="🧠 Detailed Analysis",
                border_style="magenta"
            )
            self.console.print(analysis_panel)
            self.console.print()
        
        # Significance Assessment
        if report.get('significance_assessment'):
            significance_panel = Panel(
                report['significance_assessment'],
                title="⭐ Significance Assessment",
                border_style="red"
            )
            self.console.print(significance_panel)
            self.console.print()
        
        # Related Topics
        if report.get('related_topics'):
            topics_content = "\n".join([f"• {topic}" for topic in report['related_topics']])
            topics_panel = Panel(
                topics_content,
                title="🔗 Related Topics",
                border_style="cyan"
            )
            self.console.print(topics_panel)
            self.console.print()
        
        # Conclusion
        if report.get('conclusion'):
            conclusion_panel = Panel(
                report['conclusion'],
                title="🎯 Conclusion",
                border_style="green"
            )
            self.console.print(conclusion_panel)
    
    def display_services_status(self):
        """Display status of discovered services."""
        if not self.services:
            self.console.print("[red]No services discovered[/red]")
            return
        
        status_panel = Panel(
            "\n".join([f"• {name}: [green]{url}[/green]" for name, url in self.services.items()]),
            title="🔗 Discovered Services",
            border_style="blue"
        )
        self.console.print(status_panel)