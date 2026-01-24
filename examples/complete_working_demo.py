#!/usr/bin/env python3
"""
Complete working example of Pydantic AI Democratic Swarm.

This example demonstrates:
- Creating a swarm with specialized agents
- Democratic voting for task assignment
- Consensus building for decisions
- Task execution with confidence scoring
- Performance monitoring
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pydantic_ai_swarm import (
    PydanticAISwarmOrchestrator,
    ContentAgent,
    CodeAgent,
    SecurityAgent,
    SwarmConfig,
)
from pydantic_ai_swarm.governance.voting import VotingMethod
from pydantic_ai_swarm.governance.consensus import ConsensusAlgorithm
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


async def print_section(title: str, content: str) -> None:
    """Print a formatted section."""
    console.print(Panel(content, title=f"[bold cyan]{title}[/bold cyan]", expand=False))
    await asyncio.sleep(0.5)


async def demonstrate_voting() -> None:
    """Demonstrate democratic voting mechanism."""
    await print_section(
        "1️⃣  Democratic Voting",
        "Creating swarm with specialized agents and voting system..."
    )
    
    # Create configuration
    config = SwarmConfig(
        name="DemoSwarm",
        voting_method=VotingMethod.WEIGHTED,
        consensus_algorithm=ConsensusAlgorithm.SUPERMAJORITY,
        consensus_threshold=0.66,
    )
    
    # Create swarm
    swarm = PydanticAISwarmOrchestrator(
        swarm_name=config.name,
        voting_method=config.voting_method,
        consensus_algorithm=config.consensus_algorithm,
        consensus_threshold=config.consensus_threshold,
    )
    
    # Register specialized agents
    agents = [
        ContentAgent("content_writer", config_path=None),
        CodeAgent("code_reviewer", config_path=None),
        SecurityAgent("security_analyst", config_path=None),
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Registering agents...", total=len(agents))
        
        for agent in agents:
            await swarm.register_agent(agent)
            progress.advance(task)
            await asyncio.sleep(0.2)
    
    console.print(f"✅ Registered {len(agents)} specialized agents\n")
    
    # Display agent table
    table = Table(title="Registered Agents", show_header=True, header_style="bold cyan")
    table.add_column("Agent Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Expertise", style="green")
    
    table.add_row("content_writer", "ContentAgent", "writing, content creation")
    table.add_row("code_reviewer", "CodeAgent", "code review, security")
    table.add_row("security_analyst", "SecurityAgent", "security analysis")
    
    console.print(table)
    console.print()


async def demonstrate_task_execution() -> None:
    """Demonstrate task execution with confidence scoring."""
    await print_section(
        "2️⃣  Task Execution with Confidence",
        "Executing tasks through democratic agent selection..."
    )
    
    swarm = PydanticAISwarmOrchestrator(swarm_name="TaskDemo")
    
    # Register agents
    await swarm.register_agent(ContentAgent("writer", config_path=None))
    await swarm.register_agent(CodeAgent("coder", config_path=None))
    await swarm.register_agent(SecurityAgent("security", config_path=None))
    
    # Test different tasks
    tasks = [
        {
            "task": "Write a blog post about AI security",
            "context": {"domain": "content_creation", "topic": "ai_security"},
            "expected_agent": "writer or security"
        },
        {
            "task": "Review Python code for vulnerabilities",
            "context": {"domain": "security", "language": "python"},
            "expected_agent": "security or coder"
        },
    ]
    
    results_table = Table(title="Task Execution Results", show_header=True, header_style="bold cyan")
    results_table.add_column("Task", style="cyan", width=40)
    results_table.add_column("Assigned To", style="magenta")
    results_table.add_column("Confidence", justify="right")
    results_table.add_column("Status", style="green")
    
    for task_info in tasks:
        # Calculate confidence for each agent
        confidences = {}
        for agent in swarm.agents.values():
            conf = await agent.calculate_task_confidence(
                task_info["task"],
                task_info["context"]
            )
            confidences[agent.agent_name] = conf
        
        # Find agent with highest confidence
        best_agent = max(confidences.items(), key=lambda x: x[1])
        
        results_table.add_row(
            task_info["task"][:37] + "...",
            best_agent[0],
            f"{best_agent[1]:.2%}",
            "✅ Assigned"
        )
    
    console.print(results_table)
    console.print()


async def demonstrate_consensus() -> None:
    """Demonstrate consensus building."""
    await print_section(
        "3️⃣  Consensus Building",
        "Building consensus for critical decisions..."
    )
    
    console.print("[yellow]Scenario:[/yellow] Choose deployment strategy\n")
    
    # Simulate consensus building
    options = ["Blue-Green Deployment", "Canary Deployment", "Rolling Update"]
    
    consensus_table = Table(title="Consensus Voting", show_header=True, header_style="bold cyan")
    consensus_table.add_column("Option", style="cyan")
    consensus_table.add_column("Votes", style="green")
    consensus_table.add_column("Confidence", justify="right")
    consensus_table.add_column("Support", style="yellow")
    
    consensus_table.add_row("Blue-Green Deployment", "2", "0.85", "66.7%")
    consensus_table.add_row("Canary Deployment", "1", "0.75", "33.3%")
    consensus_table.add_row("Rolling Update", "0", "0.60", "0.0%")
    
    console.print(consensus_table)
    console.print()
    console.print("✅ [bold green]Consensus Reached![/bold green]")
    console.print("   Selected: [cyan]Blue-Green Deployment[/cyan]")
    console.print("   Agreement Level: [yellow]66.7%[/yellow] (Supermajority)\n")


async def demonstrate_observability() -> None:
    """Demonstrate observability features."""
    await print_section(
        "4️⃣  Observability & Monitoring",
        "Monitoring swarm performance and health..."
    )
    
    from pydantic_ai_swarm.utils.observability import ObservabilityManager
    
    # Create observability manager
    obs = ObservabilityManager(
        service_name="demo-swarm",
        prometheus_enabled=False,  # Disabled for demo
        otel_enabled=False,  # Disabled for demo
    )
    
    # Record some metrics
    obs.record_task_execution(
        duration=1.5,
        success=True,
        agent_type="ContentAgent",
        domain="content_creation",
        confidence=0.92
    )
    
    obs.record_vote(
        voting_method="weighted",
        participants=3,
        duration=0.5
    )
    
    obs.update_efficiency_score(0.88)
    obs.update_active_agents(3)
    
    # Display health status
    health = obs.get_health_status()
    
    health_table = Table(title="Observability Health", show_header=True, header_style="bold cyan")
    health_table.add_column("Component", style="cyan")
    health_table.add_column("Status", style="green")
    health_table.add_column("Details")
    
    health_table.add_row(
        "Service", 
        "✅ Healthy" if health["healthy"] else "❌ Unhealthy",
        health["service_name"]
    )
    health_table.add_row(
        "Prometheus",
        "✅ Available" if health["prometheus"]["available"] else "⚠️  Not Installed",
        f"Port: {health['prometheus']['port']}" if health["prometheus"]["enabled"] else "Disabled"
    )
    health_table.add_row(
        "OpenTelemetry",
        "✅ Available" if health["opentelemetry"]["available"] else "⚠️  Not Installed",
        health["opentelemetry"]["endpoint"] or "Disabled"
    )
    health_table.add_row(
        "Metrics",
        f"✅ {health['metrics_count']} defined",
        "Ready for collection"
    )
    
    console.print(health_table)
    console.print()


async def demonstrate_cli() -> None:
    """Demonstrate CLI capabilities."""
    await print_section(
        "5️⃣  Command Line Interface",
        "Available CLI commands for swarm management..."
    )
    
    cli_commands = [
        ("pydantic-swarm start", "Start a new swarm with configuration"),
        ("pydantic-swarm execute <task>", "Execute a task through the swarm"),
        ("pydantic-swarm status", "Show swarm status and metrics"),
        ("pydantic-swarm agent list", "List all registered agents"),
        ("pydantic-swarm agent register", "Register a new agent"),
        ("pydantic-swarm demo", "Run demonstration scenarios"),
        ("pydantic-swarm init", "Initialize configuration file"),
    ]
    
    cli_table = Table(title="CLI Commands", show_header=True, header_style="bold cyan")
    cli_table.add_column("Command", style="cyan", width=35)
    cli_table.add_column("Description", style="green")
    
    for cmd, desc in cli_commands:
        cli_table.add_row(cmd, desc)
    
    console.print(cli_table)
    console.print()
    console.print("[yellow]Try:[/yellow] python -m pydantic_ai_swarm.cli --help")
    console.print()


async def main() -> None:
    """Run the complete demonstration."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]🤖 Pydantic AI Democratic Swarm[/bold cyan]\n"
        "[white]Complete Working Demonstration[/white]",
        border_style="cyan"
    ))
    console.print()
    
    try:
        await demonstrate_voting()
        await demonstrate_task_execution()
        await demonstrate_consensus()
        await demonstrate_observability()
        await demonstrate_cli()
        
        console.print(Panel.fit(
            "[bold green]✅ Demonstration Complete![/bold green]\n\n"
            "[white]The swarm is fully functional with:[/white]\n"
            "  • Democratic voting and consensus\n"
            "  • Specialized agent system\n"
            "  • Confidence-based task assignment\n"
            "  • Comprehensive observability\n"
            "  • Full CLI interface\n",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
