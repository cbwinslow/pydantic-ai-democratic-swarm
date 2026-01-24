#!/usr/bin/env python3
"""
Democratic Voting Example - Pydantic AI Swarm

Demonstrates the democratic voting and consensus building capabilities
of the Pydantic AI Swarm system.
"""

import asyncio
from pydantic_ai_swarm import (
    PydanticAISwarmOrchestrator,
    BaseAgent,
    ConfidenceMetrics,
    VotingMethod,
    ConsensusAlgorithm,
)
from pydantic_ai_swarm.tools.robust_tool import ToolResult


class DemoAgent(BaseAgent):
    """Demo agent for testing voting system."""
    
    def __init__(self, agent_name: str, domain_expertise: list = None):
        """Initialize demo agent.
        
        Args:
            agent_name: Name of the agent
            domain_expertise: List of domains this agent specializes in
        """
        # Initialize without config file
        self.agent_name = agent_name
        self.name = agent_name
        self.role = f"{agent_name}_role"
        self.model = "demo_model"
        self.system_prompt = f"I am {agent_name}"
        self.workflow_configs = {}
        
        # Initialize state
        self.tools = {}
        self.state = {}
        self.execution_history = []
        
        # Setup confidence with domain expertise
        self.confidence = ConfidenceMetrics()
        self.confidence.overall = 0.7
        
        domain_expertise = domain_expertise or ["general"]
        for domain in domain_expertise:
            self.confidence.domains[domain] = 0.8
        
        # Setup logging
        import logging
        self.logger = logging.getLogger(f"DemoAgent.{agent_name}")
        self.logger.setLevel(logging.INFO)
    
    def _initialize_tools(self):
        """Initialize tools (not needed for demo)."""
        return {}
    
    async def execute_task(self, task_description: str, context: dict) -> ToolResult:
        """Execute a demo task."""
        print(f"  ✓ {self.agent_name} executing: {task_description}")
        
        return ToolResult(
            success=True,
            data={
                "agent": self.agent_name,
                "task": task_description,
                "result": f"Task completed by {self.agent_name}"
            },
            execution_id=f"{self.agent_name}_task"
        )


async def demonstrate_voting_methods():
    """Demonstrate different voting methods."""
    print("\n" + "="*60)
    print("VOTING METHODS DEMONSTRATION")
    print("="*60)
    
    # Test each voting method
    voting_methods = [
        (VotingMethod.PLURALITY, "Plurality Voting (Simple Majority)"),
        (VotingMethod.WEIGHTED, "Weighted Voting (Confidence-Based)"),
        (VotingMethod.CONSENSUS, "Consensus Voting (High Agreement Required)"),
    ]
    
    for method, description in voting_methods:
        print(f"\n### {description} ###\n")
        
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name=f"VotingDemo_{method.value}",
            voting_method=method,
            consensus_threshold=0.66,
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Create agents with different expertise levels
        agents = [
            DemoAgent("DataExpert", domain_expertise=["data_analysis", "statistics"]),
            DemoAgent("CodeExpert", domain_expertise=["programming", "algorithms"]),
            DemoAgent("Generalist", domain_expertise=["general"]),
        ]
        
        # Set different confidence levels
        agents[0].confidence.overall = 0.9  # High confidence expert
        agents[1].confidence.overall = 0.7  # Moderate confidence
        agents[2].confidence.overall = 0.5  # Lower confidence
        
        # Register agents
        for agent in agents:
            await orchestrator.register_agent(agent)
        
        await orchestrator.start_swarm()
        
        # Execute a task
        result = await orchestrator.execute_task(
            "Analyze customer data trends",
            context={"domain": "data_analysis"}
        )
        
        print(f"Task assigned to: {result.agent_name}")
        print(f"Confidence score: {result.confidence_score:.2%}")
        print(f"Consensus level: {result.consensus_level:.2%}")
        
        # Show voting details
        if orchestrator.voting_history:
            vote_result = orchestrator.voting_history[-1]
            print(f"Total votes: {vote_result.total_votes}")
            print(f"Abstentions: {vote_result.abstentions}")
            print(f"Participation: {vote_result.participation_rate:.2%}")
        
        await orchestrator.stop_swarm()


async def demonstrate_consensus_building():
    """Demonstrate consensus building for decisions."""
    print("\n" + "="*60)
    print("CONSENSUS BUILDING DEMONSTRATION")
    print("="*60)
    
    # Test different consensus algorithms
    algorithms = [
        (ConsensusAlgorithm.SIMPLE_MAJORITY, "Simple Majority (>50%)"),
        (ConsensusAlgorithm.SUPERMAJORITY, "Supermajority (>66%)"),
        (ConsensusAlgorithm.QUORUM_BASED, "Quorum-Based (Minimum Participation)"),
    ]
    
    for algorithm, description in algorithms:
        print(f"\n### {description} ###\n")
        
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name=f"ConsensusDemo_{algorithm.value}",
            consensus_algorithm=algorithm,
            consensus_threshold=0.66,
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Create diverse agent team
        agents = [
            DemoAgent("SecurityExpert", domain_expertise=["security", "compliance"]),
            DemoAgent("PerformanceExpert", domain_expertise=["performance", "optimization"]),
            DemoAgent("UXExpert", domain_expertise=["user_experience", "design"]),
            DemoAgent("BusinessAnalyst", domain_expertise=["business", "strategy"]),
        ]
        
        for agent in agents:
            await orchestrator.register_agent(agent)
        
        await orchestrator.start_swarm()
        
        # Build consensus on a decision
        result = await orchestrator.build_consensus(
            proposal_title="Select cloud provider",
            proposal_description="Choose the best cloud provider for our application",
            options=["AWS", "Azure", "Google Cloud"],
            context={"domain": "infrastructure", "priority": "high"}
        )
        
        print(f"Consensus reached: {result.consensus_reached}")
        print(f"Chosen option: {result.chosen_option}")
        print(f"Agreement level: {result.agreement_level:.2%}")
        print(f"Participating agents: {len(result.participating_agents)}")
        print(f"Rounds taken: {len(result.rounds)}")
        
        await orchestrator.stop_swarm()


async def demonstrate_iterative_refinement():
    """Demonstrate iterative consensus refinement."""
    print("\n" + "="*60)
    print("ITERATIVE REFINEMENT DEMONSTRATION")
    print("="*60 + "\n")
    
    orchestrator = PydanticAISwarmOrchestrator(
        swarm_name="IterativeDemo",
        consensus_algorithm=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
        consensus_threshold=0.75,  # High threshold
        enable_diagnostics=False,
        enable_monitoring=False
    )
    
    # Create agents with varying confidence
    agents = [
        DemoAgent(f"Agent{i}", domain_expertise=["general"])
        for i in range(5)
    ]
    
    # Set different confidence levels
    for i, agent in enumerate(agents):
        agent.confidence.overall = 0.5 + (i * 0.1)
    
    for agent in agents:
        await orchestrator.register_agent(agent)
    
    await orchestrator.start_swarm()
    
    # Try to reach consensus
    print("Building consensus through multiple rounds...\n")
    
    result = await orchestrator.build_consensus(
        proposal_title="Choose development methodology",
        proposal_description="Select the best development methodology for the team",
        options=["Agile/Scrum", "Kanban", "Waterfall", "Hybrid"],
        context={"domain": "project_management"}
    )
    
    print(f"Consensus reached: {result.consensus_reached}")
    print(f"Chosen option: {result.chosen_option}")
    print(f"Agreement level: {result.agreement_level:.2%}")
    print(f"Total rounds: {len(result.rounds)}")
    
    # Show round-by-round progression
    for i, round_data in enumerate(result.rounds, 1):
        print(f"\nRound {i}:")
        print(f"  Agreement level: {round_data.agreement_level:.2%}")
        print(f"  Votes cast: {len(round_data.votes)}")
    
    await orchestrator.stop_swarm()


async def demonstrate_voting_statistics():
    """Demonstrate voting statistics and monitoring."""
    print("\n" + "="*60)
    print("VOTING STATISTICS DEMONSTRATION")
    print("="*60 + "\n")
    
    orchestrator = PydanticAISwarmOrchestrator(
        swarm_name="StatsDemo",
        voting_method=VotingMethod.WEIGHTED,
        enable_diagnostics=False,
        enable_monitoring=False
    )
    
    # Create team of agents
    agents = [
        DemoAgent("Frontend", domain_expertise=["ui", "react"]),
        DemoAgent("Backend", domain_expertise=["api", "database"]),
        DemoAgent("DevOps", domain_expertise=["deployment", "monitoring"]),
    ]
    
    for agent in agents:
        await orchestrator.register_agent(agent)
    
    await orchestrator.start_swarm()
    
    # Execute multiple tasks
    tasks = [
        ("Build user interface", {"domain": "ui"}),
        ("Design API endpoints", {"domain": "api"}),
        ("Setup CI/CD pipeline", {"domain": "deployment"}),
        ("Implement authentication", {"domain": "security"}),
        ("Optimize database queries", {"domain": "database"}),
    ]
    
    print("Executing multiple tasks...\n")
    
    for task, context in tasks:
        result = await orchestrator.execute_task(task, context)
        print(f"✓ {task[:40]:40} → {result.agent_name}")
    
    # Get statistics
    print("\n### Voting Statistics ###\n")
    
    stats = orchestrator.get_voting_statistics()
    
    print(f"Total votes conducted: {stats['voting']['total_votes']}")
    print(f"Average consensus: {stats['voting']['average_consensus']:.2%}")
    print(f"Average participation: {stats['voting']['average_participation']:.2%}")
    
    print("\nVoting method distribution:")
    for method, count in stats['voting']['method_distribution'].items():
        print(f"  {method}: {count}")
    
    print("\nRecent voting history:")
    for vote in stats['recent_voting_history'][-3:]:
        print(f"  Winner: {vote['winner']}, "
              f"Consensus: {vote['consensus_level']:.2%}, "
              f"Participation: {vote['participation_rate']:.2%}")
    
    await orchestrator.stop_swarm()


async def main():
    """Run all demonstrations."""
    print("\n" + "🤖 "*20)
    print("PYDANTIC AI SWARM - DEMOCRATIC VOTING DEMONSTRATION")
    print("🤖 "*20)
    
    try:
        # Run demonstrations
        await demonstrate_voting_methods()
        await demonstrate_consensus_building()
        await demonstrate_iterative_refinement()
        await demonstrate_voting_statistics()
        
        print("\n" + "="*60)
        print("✅ All demonstrations completed successfully!")
        print("="*60 + "\n")
        
        print("Key Takeaways:")
        print("  1. Multiple voting methods support different decision scenarios")
        print("  2. Consensus building ensures collective agreement")
        print("  3. Confidence-weighted voting leverages expertise")
        print("  4. Statistics provide visibility into decision patterns")
        print("  5. Democratic process ensures fair task assignment")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
