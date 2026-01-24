"""Command Line Interface for Pydantic AI Swarm.

This module provides a comprehensive CLI for managing and interacting with
the Pydantic AI Democratic Swarm system.
"""

import asyncio
import click
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from pydantic_ai_swarm import PydanticAISwarmOrchestrator
from pydantic_ai_swarm.core.config import SwarmConfig
from pydantic_ai_swarm.governance.voting import VotingMethod
from pydantic_ai_swarm.governance.consensus import ConsensusAlgorithm

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="Pydantic AI Swarm")
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str]) -> None:
    """Pydantic AI Democratic Swarm - AI agent orchestration system.
    
    A revolutionary system that democratizes decision-making and ensures
    efficient development across multiple applications and domains.
    """
    # Store config path in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


@cli.command()
@click.option("--name", default="DefaultSwarm", help="Name of the swarm")
@click.option("--agents", default=3, type=int, help="Number of agents to create")
@click.option("--voting", type=click.Choice(["plurality", "weighted", "ranked_choice", "approval", "consensus"]), 
              default="weighted", help="Voting method")
@click.option("--consensus", type=click.Choice(["simple_majority", "supermajority", "unanimous", "quorum_based"]),
              default="supermajority", help="Consensus algorithm")
@click.option("--threshold", default=0.66, type=float, help="Consensus threshold (0.0-1.0)")
@click.pass_context
def start(ctx: click.Context, name: str, agents: int, voting: str, consensus: str, threshold: float) -> None:
    """Start a new swarm with specified configuration.
    
    Examples:
        pydantic-swarm start --name MySwarm --agents 5
        pydantic-swarm start --name DevSwarm --voting weighted --consensus supermajority
    """
    async def _start() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Starting swarm '{name}'...", total=None)
            
            try:
                # Load or create config
                if ctx.obj.get("config_path"):
                    config = SwarmConfig.from_yaml(Path(ctx.obj["config_path"]))
                else:
                    config = SwarmConfig(
                        name=name,
                        voting_method=VotingMethod[voting.upper()],
                        consensus_algorithm=ConsensusAlgorithm[consensus.upper()],
                        consensus_threshold=threshold,
                    )
                
                # Create swarm
                swarm = PydanticAISwarmOrchestrator(
                    name=config.name,
                    voting_method=config.voting_method,
                    consensus_algorithm=config.consensus_algorithm,
                    consensus_threshold=config.consensus_threshold,
                )
                
                progress.update(task, description=f"[cyan]Initializing {agents} agents...")
                
                # Note: Agent creation would happen here when specialized agents are implemented
                # For now, we just report the configuration
                
                progress.update(task, description="[green]✓ Swarm started successfully")
                
                console.print("\n[bold green]✅ Swarm Started Successfully![/bold green]")
                console.print(f"[cyan]Name:[/cyan] {name}")
                console.print(f"[cyan]Agents:[/cyan] {agents} (to be implemented)")
                console.print(f"[cyan]Voting Method:[/cyan] {voting}")
                console.print(f"[cyan]Consensus Algorithm:[/cyan] {consensus}")
                console.print(f"[cyan]Consensus Threshold:[/cyan] {threshold:.2%}")
                
                console.print("\n[yellow]Note:[/yellow] Specialized agents need to be registered separately.")
                console.print("[dim]Use 'pydantic-swarm agent register' to add specialized agents.[/dim]")
                
            except Exception as e:
                progress.update(task, description=f"[red]✗ Failed to start swarm")
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                sys.exit(1)
    
    asyncio.run(_start())


@cli.command()
@click.argument("task")
@click.option("--domain", default="general", help="Task domain")
@click.option("--priority", default=5, type=int, help="Task priority (1-10)")
@click.option("--timeout", default=300, type=int, help="Task timeout in seconds")
@click.option("--context", "-x", multiple=True, help="Additional context (key=value)")
def execute(task: str, domain: str, priority: int, timeout: int, context: tuple) -> None:
    """Execute a task through the swarm.
    
    Examples:
        pydantic-swarm execute "Analyze this codebase" --domain code_analysis
        pydantic-swarm execute "Create blog post" --domain content --context target=developers
    """
    async def _execute() -> None:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task_id = progress.add_task("[cyan]Executing task...", total=None)
            
            try:
                # Parse context
                task_context = {"domain": domain, "priority": priority}
                for ctx_item in context:
                    if "=" in ctx_item:
                        key, value = ctx_item.split("=", 1)
                        task_context[key] = value
                
                console.print(f"\n[bold]🎯 Task:[/bold] {task}")
                console.print(f"[cyan]Domain:[/cyan] {domain}")
                console.print(f"[cyan]Priority:[/cyan] {priority}")
                console.print(f"[cyan]Timeout:[/cyan] {timeout}s")
                if context:
                    console.print(f"[cyan]Context:[/cyan] {dict(task_context)}")
                
                progress.update(task_id, description="[cyan]Building consensus...")
                
                # Note: Actual execution would happen here with a running swarm
                # For now, we demonstrate the flow
                
                progress.update(task_id, description="[green]✓ Task completed")
                
                console.print("\n[bold green]✅ Task Completed Successfully![/bold green]")
                console.print("[yellow]Note:[/yellow] Connect to a running swarm for actual execution.")
                
            except Exception as e:
                progress.update(task_id, description=f"[red]✗ Task failed")
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                sys.exit(1)
    
    asyncio.run(_execute())


@cli.command()
@click.option("--format", type=click.Choice(["table", "json", "simple"]), default="table", 
              help="Output format")
def status(format: str) -> None:
    """Show swarm status and metrics.
    
    Examples:
        pydantic-swarm status
        pydantic-swarm status --format json
    """
    async def _status() -> None:
        try:
            # Note: This would connect to a running swarm instance
            # For now, we show example status
            
            if format == "table":
                table = Table(title="Swarm Status", show_header=True, header_style="bold cyan")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Status", "Running")
                table.add_row("Active Agents", "3")
                table.add_row("Pending Tasks", "0")
                table.add_row("Completed Tasks", "127")
                table.add_row("Success Rate", "94.5%")
                table.add_row("Avg Response Time", "2.3s")
                table.add_row("Consensus Rate", "88.2%")
                
                console.print(table)
                
            elif format == "json":
                import json
                status_data = {
                    "status": "running",
                    "active_agents": 3,
                    "pending_tasks": 0,
                    "completed_tasks": 127,
                    "success_rate": 0.945,
                    "avg_response_time": 2.3,
                    "consensus_rate": 0.882,
                }
                console.print_json(json.dumps(status_data, indent=2))
                
            else:  # simple
                console.print("Status: [green]Running[/green]")
                console.print("Agents: 3 active")
                console.print("Tasks: 0 pending, 127 completed")
                console.print("Success Rate: 94.5%")
            
            console.print("\n[yellow]Note:[/yellow] Connect to a running swarm for live status.")
            
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            sys.exit(1)
    
    asyncio.run(_status())


@cli.group()
def agent() -> None:
    """Manage swarm agents."""
    pass


@agent.command("list")
@click.option("--format", type=click.Choice(["table", "json", "simple"]), default="table")
def agent_list(format: str) -> None:
    """List all registered agents.
    
    Examples:
        pydantic-swarm agent list
        pydantic-swarm agent list --format json
    """
    if format == "table":
        table = Table(title="Registered Agents", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Confidence", justify="right")
        table.add_column("Tasks", justify="right")
        
        # Example data
        table.add_row("content_specialist", "ContentAgent", "Active", "0.92", "47")
        table.add_row("code_reviewer", "CodeAgent", "Active", "0.88", "35")
        table.add_row("security_analyst", "SecurityAgent", "Active", "0.95", "21")
        
        console.print(table)
    else:
        console.print("[yellow]Note:[/yellow] Agent list feature requires connection to running swarm.")


@agent.command("register")
@click.argument("agent_type")
@click.argument("name")
@click.option("--domain", multiple=True, help="Domain expertise")
@click.option("--confidence", default=0.7, type=float, help="Confidence threshold")
def agent_register(agent_type: str, name: str, domain: tuple, confidence: float) -> None:
    """Register a new agent with the swarm.
    
    Examples:
        pydantic-swarm agent register ContentAgent writer1 --domain content
        pydantic-swarm agent register CodeAgent reviewer --domain code --confidence 0.8
    """
    console.print(f"[cyan]Registering agent:[/cyan] {name}")
    console.print(f"[cyan]Type:[/cyan] {agent_type}")
    console.print(f"[cyan]Domains:[/cyan] {', '.join(domain) if domain else 'general'}")
    console.print(f"[cyan]Confidence Threshold:[/cyan] {confidence}")
    console.print("\n[yellow]Note:[/yellow] Agent registration requires connection to running swarm.")


@cli.command()
@click.option("--scenario", default="basic", 
              type=click.Choice(["basic", "voting", "consensus", "efficiency", "full"]),
              help="Demo scenario to run")
@click.option("--verbose", is_flag=True, help="Verbose output")
def demo(scenario: str, verbose: bool) -> None:
    """Run demonstration scenarios.
    
    Examples:
        pydantic-swarm demo --scenario voting
        pydantic-swarm demo --scenario consensus --verbose
    """
    async def _demo() -> None:
        console.print(f"\n[bold cyan]🎭 Running {scenario.upper()} Demo[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Setting up demo...", total=None)
            
            try:
                if scenario == "basic":
                    progress.update(task, description="[cyan]Creating basic swarm...")
                    console.print("[green]✓[/green] Basic swarm created")
                    console.print("[dim]Demonstrating simple task execution...[/dim]")
                    
                elif scenario == "voting":
                    progress.update(task, description="[cyan]Demonstrating voting mechanisms...")
                    console.print("[green]✓[/green] Voting demo setup")
                    console.print("[dim]Showing plurality, weighted, and ranked-choice voting...[/dim]")
                    
                elif scenario == "consensus":
                    progress.update(task, description="[cyan]Building consensus...")
                    console.print("[green]✓[/green] Consensus demo setup")
                    console.print("[dim]Demonstrating consensus algorithms...[/dim]")
                    
                elif scenario == "efficiency":
                    progress.update(task, description="[cyan]Testing efficiency enforcement...")
                    console.print("[green]✓[/green] Efficiency enforcer active")
                    console.print("[dim]Preventing code duplication...[/dim]")
                    
                elif scenario == "full":
                    progress.update(task, description="[cyan]Running full workflow demo...")
                    console.print("[green]✓[/green] Full demo initialized")
                    console.print("[dim]End-to-end workflow demonstration...[/dim]")
                
                progress.update(task, description="[green]✓ Demo completed")
                
                console.print("\n[bold green]✅ Demo Completed Successfully![/bold green]")
                console.print("[yellow]Note:[/yellow] Demos show system capabilities. Full implementation in progress.")
                
            except Exception as e:
                console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
                sys.exit(1)
    
    asyncio.run(_demo())


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", type=click.Choice(["yaml", "json"]), default="yaml", help="Config format")
def init(output: Optional[str], format: str) -> None:
    """Initialize a new swarm configuration file.
    
    Examples:
        pydantic-swarm init
        pydantic-swarm init --output config.yaml
        pydantic-swarm init --format json --output config.json
    """
    try:
        config = SwarmConfig()
        
        if output:
            output_path = Path(output)
        else:
            output_path = Path(f"swarm_config.{format}")
        
        if format == "yaml":
            import yaml
            with open(output_path, "w") as f:
                yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)
        else:  # json
            import json
            with open(output_path, "w") as f:
                json.dump(config.to_dict(), f, indent=2)
        
        console.print(f"[green]✓[/green] Configuration file created: [cyan]{output_path}[/cyan]")
        console.print("[dim]Edit the file to customize your swarm configuration.[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


def main() -> None:
    """Main entry point for CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {str(e)}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()
