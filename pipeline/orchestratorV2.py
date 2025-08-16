"""
Pipeline Orchestrator V2 - AI SEO Blog Generator
Production-ready version with all real agents
Beautiful terminal output with progress tracking
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import ALL REAL agents
from agents.market_search import MarketResearchAgent
from agents.keyword_analyzer import KeywordAnalyzerAgent  
from agents.content_planner import ContentPlannerAgent
from agents.seo_optimizer import SEOOptimizerAgent
from agents.content_writer import ContentWriterAgent
from agents.quality_check import QualityCheckerAgent
from agents.publisher import PublisherAgent

# Import services
from services.gemini_service import GeminiService
from services.seo_tools import SEOToolsService

# Beautiful console output
try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Installing rich for beautiful output...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.live import Live
    from rich.layout import Layout
    RICH_AVAILABLE = True


@dataclass
class PipelineConfig:
    """Pipeline configuration"""
    # Required fields
    product_name: str
    niche: str
    target_audience: str
    
    # Optional fields with defaults
    target_keywords: List[str] = field(default_factory=lambda: ["seo", "blog", "content"])
    content_length: str = "2000-2500 words"
    budget: float = 2000.0
    
    # WordPress settings
    wordpress_url: str = "http://localhost/wordpress"
    wordpress_username: str = "admin"
    wordpress_password: str = ""
    publish_status: str = "draft"  # draft or publish
    
    # Pipeline settings
    skip_quality_check: bool = True  # Skip quality check to save API calls
    skip_publishing: bool = False  # Skip WordPress publishing


class PipelineOrchestrator:
    """
    🎭 Main Pipeline Orchestrator
    Manages all 7 agents in sequence
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.console = Console()
        self.logger = self._setup_logger()
        
        # Services
        self.gemini = GeminiService()
        self.seo_tools = SEOToolsService()
        
        # Results storage
        self.pipeline_data = {}
        self.agent_results = {}
        self.errors = []
        
        # Timing
        self.start_time = None
        self.end_time = None
        
        # Initialize agents
        self._initialize_agents()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logger"""
        logger = logging.getLogger("Pipeline")
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler('pipeline.log')
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
        
    def _initialize_agents(self):
        """Initialize all agents with proper configuration"""
        self.console.print("\n[bold cyan]🚀 Initializing AI Agents...[/bold cyan]")
        
        # WordPress config for publisher
        wp_config = {
            "url": self.config.wordpress_url,
            "username": self.config.wordpress_username,
            "password": self.config.wordpress_password
        }
        
        # Create agent instances
        self.agents = {
            "1_market_research": MarketResearchAgent(self.gemini),
            "2_keyword_analyzer": KeywordAnalyzerAgent(self.gemini, self.seo_tools),
            "3_content_planner": ContentPlannerAgent(self.gemini),
            "4_seo_optimizer": SEOOptimizerAgent(self.gemini),
            "5_content_writer": ContentWriterAgent(self.gemini),
            "6_quality_checker": QualityCheckerAgent(self.gemini),
            "7_publisher": PublisherAgent(self.gemini, wp_config)
        }
        
        # Set callbacks
        for name, agent in self.agents.items():
            agent.set_progress_callback(self._progress_callback)
            
        self.console.print("[green]✅ All agents initialized successfully![/green]\n")
        
    def _progress_callback(self, agent_name: str, progress: int, status: str, current_step: str):
        """Progress callback for agents"""
        # Simple console output for now
        icon = "⚙️" if status == "processing" else "✅" if status == "completed" else "🔄"
        self.console.print(f"  {icon} [{progress:3d}%] {current_step}", end="\r")
        
    async def run_pipeline(self) -> Dict[str, Any]:
        """
        🎬 Run the complete pipeline
        """
        self.start_time = datetime.now()
        
        # Print header
        self._print_header()
        
        # Initialize pipeline data
        self.pipeline_data = {
            "product_name": self.config.product_name,
            "niche": self.config.niche,
            "target_audience": self.config.target_audience,
            "target_keywords": self.config.target_keywords,
            "content_length": self.config.content_length,
            "budget": self.config.budget
        }
        
        # Progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            # Add main task
            main_task = progress.add_task("[cyan]Pipeline Progress", total=7)
            
            # Execute each agent
            agent_names = [
                ("1_market_research", "🔍 Market Research", "Analyzing market and competition..."),
                ("2_keyword_analyzer", "🔑 Keyword Analysis", "Finding best keywords..."),
                ("3_content_planner", "📋 Content Planning", "Creating content structure..."),
                ("4_seo_optimizer", "🎯 SEO Optimization", "Optimizing for search engines..."),
                ("5_content_writer", "✍️ Content Writing", "Writing the article..."),
                ("6_quality_checker", "✨ Quality Check", "Checking content quality..."),
                ("7_publisher", "🚀 Publishing", "Publishing to WordPress...")
            ]
            
            for agent_key, display_name, description in agent_names:
                # Skip certain agents if configured
                if agent_key == "6_quality_checker" and self.config.skip_quality_check:
                    self.console.print(f"\n[yellow]⏭️ Skipping {display_name}[/yellow]")
                    progress.update(main_task, advance=1)
                    continue
                    
                if agent_key == "7_publisher" and self.config.skip_publishing:
                    self.console.print(f"\n[yellow]⏭️ Skipping {display_name}[/yellow]")
                    progress.update(main_task, advance=1)
                    continue
                
                # Print stage header    
                self.console.print(f"\n[bold blue]{display_name}[/bold blue]")
                self.console.print(f"[dim]{description}[/dim]")
                
                try:
                    # Execute agent
                    agent = self.agents[agent_key]
                    result = await agent.execute(self.pipeline_data)
                    
                    if result.success:
                        # Store results
                        self.agent_results[agent_key] = result
                        self.pipeline_data[agent_key.split('_', 1)[1]] = result.data
                        
                        # Success message
                        self.console.print(f"[green]✅ {display_name} completed![/green]")
                        
                        # Show key metrics
                        if agent_key == "2_keyword_analyzer":
                            summary = result.data.get("analysis_summary", {})
                            self.console.print(f"   [dim]Found {summary.get('total_keywords_analyzed', 0)} keywords[/dim]")
                        elif agent_key == "5_content_writer":
                            summary = result.data.get("writing_summary", {})
                            self.console.print(f"   [dim]Wrote {summary.get('total_word_count', 0)} words[/dim]")
                        elif agent_key == "7_publisher":
                            pub_summary = result.data.get("publication_summary", {})
                            if pub_summary.get("post_id"):
                                self.console.print(f"   [dim]Post ID: {pub_summary['post_id']}[/dim]")
                                self.console.print(f"   [dim]URL: {pub_summary.get('post_url', 'N/A')}[/dim]")
                    else:
                        # Failure
                        self.errors.append(f"{display_name} failed: {result.errors}")
                        self.console.print(f"[red]❌ {display_name} failed![/red]")
                        
                        # Continue anyway
                        if agent_key not in ["5_content_writer", "7_publisher"]:
                            self.console.print("[yellow]   Continuing with limited data...[/yellow]")
                        
                except Exception as e:
                    self.errors.append(f"{display_name} exception: {str(e)}")
                    self.console.print(f"[red]❌ {display_name} crashed: {str(e)}[/red]")
                    self.logger.error(f"{agent_key} exception", exc_info=True)
                    
                    # Critical agents - stop if they fail
                    if agent_key in ["5_content_writer"]:
                        self.console.print("[red]⛔ Cannot continue without content![/red]")
                        break
                
                # Update progress
                progress.update(main_task, advance=1)
        
        # Finalize
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Print summary
        self._print_summary(duration)
        
        # Save results
        self._save_results()
        
        return {
            "success": len(self.errors) == 0,
            "duration": duration,
            "agents_completed": len(self.agent_results),
            "errors": self.errors,
            "pipeline_data": self.pipeline_data,
            "agent_results": self.agent_results
        }
    
    def _print_header(self):
        """Print beautiful header"""
        header_text = f"""[bold cyan]🎯 AI SEO BLOG GENERATOR[/bold cyan]
        
[yellow]Product:[/yellow] {self.config.product_name}
[yellow]Niche:[/yellow] {self.config.niche}  
[yellow]Audience:[/yellow] {self.config.target_audience}
[yellow]Keywords:[/yellow] {', '.join(self.config.target_keywords[:3])}"""
        
        panel = Panel(header_text, title="Pipeline Configuration", border_style="cyan")
        self.console.print(panel)
        
    def _print_summary(self, duration: float):
        """Print execution summary"""
        
        # Check for WordPress results
        wp_info = ""
        if "7_publisher" in self.agent_results:
            pub_data = self.agent_results["7_publisher"].data
            pub_summary = pub_data.get("publication_summary", {})
            if pub_summary.get("post_id"):
                wp_info = f"""
[green]📝 WordPress Post ID:[/green] {pub_summary['post_id']}
[green]🔗 Post URL:[/green] {pub_summary.get('post_url', 'N/A')}
[green]✏️ Edit URL:[/green] {pub_summary.get('edit_url', 'N/A')}"""
        
        # Create summary text
        if len(self.errors) == 0:
            summary_text = f"""[bold green]🎉 PIPELINE COMPLETED SUCCESSFULLY![/bold green]
            
[green]✅ Agents Completed:[/green] {len(self.agent_results)}/7
[green]⏱️ Duration:[/green] {duration:.2f} seconds
{wp_info}

[bold yellow]Your AI-generated blog post is ready! 🎊[/bold yellow]"""
            border_style = "green"
            title = "✨ Success ✨"
        else:
            summary_text = f"""[bold yellow]⚠️ PIPELINE COMPLETED WITH ISSUES[/bold yellow]
            
[yellow]✅ Agents Completed:[/yellow] {len(self.agent_results)}/7
[yellow]❌ Errors:[/yellow] {len(self.errors)}
[yellow]⏱️ Duration:[/yellow] {duration:.2f} seconds
{wp_info}

[dim]Check pipeline.log for details[/dim]"""
            border_style = "yellow"
            title = "⚠️ Partial Success ⚠️"
        
        panel = Panel(summary_text, title=title, border_style=border_style)
        self.console.print("\n")
        self.console.print(panel)
        
    def _save_results(self):
        """Save results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"pipeline_results_{timestamp}.json"
        
        # Prepare data
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "product_name": self.config.product_name,
                "niche": self.config.niche,
                "target_audience": self.config.target_audience,
                "keywords": self.config.target_keywords
            },
            "execution": {
                "duration": (self.end_time - self.start_time).total_seconds() if self.end_time else 0,
                "agents_completed": len(self.agent_results),
                "errors": self.errors
            },
            "wordpress": {}
        }
        
        # Add WordPress info if available
        if "7_publisher" in self.agent_results:
            pub_data = self.agent_results["7_publisher"].data
            pub_summary = pub_data.get("publication_summary", {})
            save_data["wordpress"] = {
                "post_id": pub_summary.get("post_id"),
                "post_url": pub_summary.get("post_url"),
                "edit_url": pub_summary.get("edit_url"),
                "status": pub_summary.get("status")
            }
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"\n[dim]Results saved to {filename}[/dim]")


async def main():
    """Main entry point"""
    
    console = Console()
    
    # Print welcome
    console.print("\n[bold magenta]🎨 AI SEO Blog Generator - Production Pipeline[/bold magenta]\n")
    
    # Configuration - CHANGE THESE VALUES!
    config = PipelineConfig(
        # Product info
        product_name="Wireless Gaming Headset Pro",
        niche="Gaming Accessories",
        target_audience="Gamers and gaming enthusiasts aged 18-35",
        target_keywords=[
            "wireless gaming headset",
            "best gaming headset 2024",
            "gaming audio equipment"
        ],
        
        # Content settings
        content_length="2000-2500 words",
        budget=3000,
        
        # WordPress settings
        wordpress_url="http://localhost/wordpress",
        wordpress_username="admin",
        wordpress_password="2025*Ommer.",  # YOUR PASSWORD HERE
        publish_status="draft",  # "draft" or "publish"
        
        # Pipeline settings
        skip_quality_check=False,  # Set True to save API calls
        skip_publishing=False  # Set True to skip WordPress
    )
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator(config)
    
    # Run pipeline
    try:
        console.print("[bold cyan]Starting pipeline execution...[/bold cyan]\n")
        result = await orchestrator.run_pipeline()
        
        if result["success"]:
            console.print("\n[bold green]🎊 Pipeline completed successfully![/bold green]")
        else:
            console.print("\n[bold yellow]⚠️ Pipeline completed with some issues.[/bold yellow]")
            console.print("[dim]Check pipeline.log for details[/dim]")
            
    except KeyboardInterrupt:
        console.print("\n[red]⛔ Pipeline interrupted by user[/red]")
    except Exception as e:
        console.print(f"\n[red]❌ Pipeline failed: {str(e)}[/red]")
        logging.error("Pipeline failed", exc_info=True)


if __name__ == "__main__":
    # Run the pipeline
    asyncio.run(main())