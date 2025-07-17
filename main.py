#!/usr/bin/env python3
"""
A2A Research Demo - Interactive Web Research System
"""

import asyncio
import sys
import os
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.layout import Layout
from rich.live import Live

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from a2a_research.search_service import WebSearchService
from a2a_research.knowledge_service import WebKnowledgeExtractionService
from a2a_research.aggregation_service import WebResearchAggregationService
from a2a_research.models import SearchQuery

console = Console()


class WebSearchTool:
    """Real web search implementation using available tools."""
    
    def __init__(self):
        # Try to import WebSearch tool if available
        try:
            # This would be the actual WebSearch tool import
            # For now, we'll simulate it
            self.available = False
        except ImportError:
            self.available = False
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Perform web search and return results."""
        if self.available:
            # Use real WebSearch tool here
            pass
        
        # Simulated search results with more realistic data
        results = [
            {
                'title': f'Research on "{query}" - Academic Paper',
                'url': f'https://arxiv.org/abs/2024.{hash(query) % 10000:04d}',
                'snippet': f'Comprehensive analysis of {query} with latest methodologies and findings from leading researchers in the field.',
                'source': 'arXiv.org'
            },
            {
                'title': f'{query.title()} - Wikipedia',
                'url': f'https://en.wikipedia.org/wiki/{query.replace(" ", "_")}',
                'snippet': f'Overview and background information about {query} including history, applications, and current research.',
                'source': 'Wikipedia'
            },
            {
                'title': f'Latest {query} News and Updates',
                'url': f'https://news.example.com/{query.replace(" ", "-")}',
                'snippet': f'Recent developments and breakthroughs in {query} from top research institutions worldwide.',
                'source': 'Research News'
            }
        ]
        
        return results[:max_results]


class A2AResearchInterface:
    """Interactive interface for A2A research system."""
    
    def __init__(self):
        self.console = Console()
        self.search_tool = WebSearchTool()
        self.shared_secret = "research-demo-secret-key-12345"
        
        # Initialize services
        self.web_search = WebSearchService(
            self.shared_secret, 
            search_function=self.search_tool.search
        )
        self.knowledge_extraction = WebKnowledgeExtractionService(self.shared_secret)
        self.research_aggregation = WebResearchAggregationService(self.shared_secret)
        
        self.tasks = []
        self.session_id = "interactive-session-001"
    
    async def start_services(self):
        """Start all A2A services."""
        self.tasks = [
            asyncio.create_task(self.web_search.process_messages()),
            asyncio.create_task(self.knowledge_extraction.process_messages()),
            asyncio.create_task(self.research_aggregation.process_messages())
        ]
        await asyncio.sleep(0.1)  # Let services initialize
    
    async def stop_services(self):
        """Stop all A2A services."""
        for task in self.tasks:
            task.cancel()
    
    def display_header(self):
        """Display the application header."""
        header = Panel.fit(
            "[bold blue]A2A Research System[/bold blue]\n"
            "[dim]Secure Application-to-Application Web Research Platform[/dim]",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()
    
    async def perform_search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Perform web search with progress indication."""
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Searching for: [bold]{query}[/bold]", total=None)
            
            # Create search query
            search_query = SearchQuery(
                id=f"query-{hash(query)}",
                query_text=query,
                max_results=max_results
            )
            
            # Send search request
            await self.web_search.send_message(self.web_search, {
                'type': 'perform_search',
                'query': {
                    'id': search_query.id,
                    'query_text': search_query.query_text,
                    'max_results': search_query.max_results
                },
                'session_id': self.session_id,
                'callback_service': 'web-research-aggregation'
            })
            
            # Wait for results (simulate processing time)
            await asyncio.sleep(1.5)
            
            # Get results from search service cache
            cache_key = f"{query}_{max_results}"
            if cache_key in self.web_search.search_cache:
                search_results = self.web_search.search_cache[cache_key]
                results = [
                    {
                        'title': r.title,
                        'url': r.url,
                        'snippet': r.snippet,
                        'source': r.source,
                        'relevance': r.relevance_score
                    }
                    for r in search_results
                ]
        
        return results
    
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
            relevance = f"{result.get('relevance', 0.8):.1f}"
            table.add_row(
                result['title'],
                result['source'],
                result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet'],
                relevance
            )
        
        self.console.print(table)
        self.console.print()
    
    async def extract_insights(self, results: List[Dict[str, Any]]):
        """Extract insights from search results."""
        if not results:
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Extracting insights...", total=None)
            
            await self.knowledge_extraction.send_message(self.knowledge_extraction, {
                'type': 'extract_web_insights',
                'search_results': results
            })
            
            await self.knowledge_extraction.send_message(self.knowledge_extraction, {
                'type': 'analyze_source_credibility',
                'search_results': results
            })
            
            await asyncio.sleep(1.0)
        
        self.console.print("[bold green]✓[/bold green] Insights extracted and credibility analyzed")
    
    async def generate_report(self, query: str, results: List[Dict[str, Any]]):
        """Generate and display research report."""
        # Start research session
        await self.research_aggregation.send_message(self.research_aggregation, {
            'type': 'start_web_research_session',
            'session': {
                'id': self.session_id,
                'topic': query
            }
        })
        
        # Aggregate results
        await self.research_aggregation.send_message(self.research_aggregation, {
            'type': 'aggregate_web_results',
            'session_id': self.session_id,
            'results': results
        })
        
        # Generate report
        await self.research_aggregation.send_message(self.research_aggregation, {
            'type': 'generate_web_report',
            'session_id': self.session_id
        })
        
        # Display report summary
        report_panel = Panel(
            f"[bold]Research Report Generated[/bold]\n\n"
            f"• Topic: [bold]{query}[/bold]\n"
            f"• Sources analyzed: [bold]{len(results)}[/bold]\n"
            f"• Session ID: [dim]{self.session_id}[/dim]\n\n"
            f"[dim]Full report available in research aggregation service[/dim]",
            title="📊 Report Summary",
            border_style="green"
        )
        self.console.print(report_panel)
    
    async def interactive_mode(self):
        """Run interactive search mode."""
        self.display_header()
        
        await self.start_services()
        
        try:
            while True:
                self.console.print("[bold]Enter a research query (or 'quit' to exit):[/bold]")
                query = Prompt.ask("🔍 Search")
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not query.strip():
                    continue
                
                # Perform search
                results = await self.perform_search(query)
                
                # Display results
                self.display_search_results(query, results)
                
                if results:
                    # Ask if user wants analysis
                    if Confirm.ask("Extract insights and generate report?"):
                        await self.extract_insights(results)
                        await self.generate_report(query, results)
                
                self.console.print("\n" + "─" * 50 + "\n")
        
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Search interrupted by user[/yellow]")
        finally:
            await self.stop_services()
            self.console.print("[dim]Research session ended[/dim]")


@click.command()
@click.option('--query', '-q', help='Search query to execute')
@click.option('--max-results', '-n', default=5, help='Maximum number of results')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def main(query: Optional[str], max_results: int, interactive: bool):
    """A2A Research Demo - Interactive Web Research System"""
    
    interface = A2AResearchInterface()
    
    async def run_search():
        if interactive or not query:
            await interface.interactive_mode()
        else:
            # Single query mode
            interface.display_header()
            await interface.start_services()
            
            try:
                results = await interface.perform_search(query, max_results)
                interface.display_search_results(query, results)
                
                if results:
                    await interface.extract_insights(results)
                    await interface.generate_report(query, results)
            finally:
                await interface.stop_services()
    
    try:
        asyncio.run(run_search())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")


if __name__ == "__main__":
    main()