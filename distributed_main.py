#!/usr/bin/env python3
"""
Distributed A2A Research Demo - True A2A with separate server processes.
"""

import asyncio
import sys
import os
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.distributed_client import DistributedA2AClient

console = Console()


class DistributedA2AInterface:
    """Interactive interface for distributed A2A research system."""
    
    def __init__(self, registry_url: str = "http://127.0.0.1:8000"):
        self.console = Console()
        self.client = DistributedA2AClient(registry_url=registry_url)
    
    def display_header(self):
        """Display the application header."""
        header = Panel.fit(
            "[bold blue]Distributed A2A Research System[/bold blue]\n"
            "[dim]True Application-to-Application Communication with Separate Services[/dim]",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()
    
    async def initialize_client(self) -> bool:
        """Initialize the distributed client."""
        self.console.print("[dim]Discovering services...[/dim]")
        
        if await self.client.discover_services():
            self.client.display_services_status()
            return True
        else:
            self.console.print("[red]Failed to discover services. Make sure all services are running.[/red]")
            self.console.print("\nTo start services, run: [bold]make start-services[/bold]")
            return False
    
    async def perform_distributed_research(self, query: str, max_results: int = 5):
        """Perform distributed research workflow."""
        try:
            # 1. Start research session
            self.console.print(f"[bold]Starting research session:[/bold] {query}")
            session_id = await self.client.start_research_session(query)
            self.console.print(f"[dim]Session ID: {session_id}[/dim]\n")
            
            # 2. Perform distributed search
            search_results = await self.client.perform_distributed_search(query, max_results)
            self.client.display_search_results(query, search_results)
            
            if not search_results:
                return
            
            # 3. Extract insights
            insights_data = await self.client.extract_insights(search_results)
            self.client.display_insights(insights_data)
            
            # 4. Analyze credibility
            credibility_data = await self.client.analyze_credibility(search_results)
            self.client.display_credibility(credibility_data)
            
            # 5. Aggregate results
            await self.client.aggregate_results(session_id, search_results)
            
            # 6. Generate report
            report = await self.client.generate_report(session_id)
            self.client.display_report(report)
            
        except Exception as e:
            self.console.print(f"[red]Error during research workflow: {e}[/red]")
    
    async def interactive_mode(self):
        """Run interactive research mode."""
        self.display_header()
        
        if not await self.initialize_client():
            return
        
        try:
            while True:
                self.console.print("\n[bold]Enter a research query (or 'quit' to exit):[/bold]")
                query = Prompt.ask("🔍 Search")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query.strip():
                    continue
                
                await self.perform_distributed_research(query)
                
                self.console.print("\n" + "─" * 50 + "\n")
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Search interrupted by user[/yellow]")
        finally:
            self.console.print("[dim]Distributed research session ended[/dim]")
    
    async def single_query_mode(self, query: str, max_results: int):
        """Run single query mode."""
        self.display_header()
        
        if not await self.initialize_client():
            return
        
        await self.perform_distributed_research(query, max_results)


@click.command()
@click.option('--query', '-q', help='Search query to execute')
@click.option('--max-results', '-n', default=5, help='Maximum number of results')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
@click.option('--registry-url', default='http://127.0.0.1:8000', help='Service registry URL')
def main(query: Optional[str], max_results: int, interactive: bool, registry_url: str):
    """Distributed A2A Research Demo - True A2A Communication"""
    
    interface = DistributedA2AInterface(registry_url=registry_url)
    
    async def run_research():
        if interactive or not query:
            await interface.interactive_mode()
        else:
            await interface.single_query_mode(query, max_results)
    
    try:
        asyncio.run(run_research())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")


if __name__ == "__main__":
    main()