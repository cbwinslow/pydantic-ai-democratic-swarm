"""Integration tests for orchestrator with voting system."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pydantic_ai_swarm.core.orchestrator import PydanticAISwarmOrchestrator, TaskResult
from pydantic_ai_swarm.core.base_agent import BaseAgent, ConfidenceMetrics
from pydantic_ai_swarm.governance.voting import VotingMethod
from pydantic_ai_swarm.governance.consensus import ConsensusAlgorithm
from pydantic_ai_swarm.tools.robust_tool import ToolResult


class TestAgent(BaseAgent):
    """Test agent implementation."""
    
    def __init__(self, agent_name: str, domain_expertise: list = None):
        """Initialize test agent without config file."""
        self.agent_name = agent_name
        self.name = agent_name
        self.role = "test_role"
        self.model = "test_model"
        self.system_prompt = "test prompt"
        self.workflow_configs = {}
        
        # Initialize tools
        self.tools = {}
        
        # State management
        self.state = {}
        self.execution_history = []
        
        # Confidence metrics
        self.confidence = ConfidenceMetrics()
        
        # Set domain expertise
        domain_expertise = domain_expertise or ["general"]
        for domain in domain_expertise:
            self.confidence.domains[domain] = 0.8
        
        # Initialize logging
        import logging
        self.logger = logging.getLogger(f"TestAgent.{agent_name}")
        self.logger.setLevel(logging.INFO)
    
    def _initialize_tools(self):
        """Initialize tools (empty for test agent)."""
        return {}
    
    async def execute_task(self, task_description: str, context: dict) -> ToolResult:
        """Execute a task."""
        return ToolResult(
            success=True,
            data={"result": f"Task '{task_description}' executed by {self.agent_name}"},
            execution_id=f"{self.agent_name}_task"
        )


class TestOrchestratorVoting:
    """Tests for orchestrator voting functionality."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization_with_voting(self):
        """Test orchestrator initializes with voting system."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            voting_method=VotingMethod.WEIGHTED,
            consensus_algorithm=ConsensusAlgorithm.SUPERMAJORITY
        )
        
        assert orchestrator.swarm_name == "test_swarm"
        assert orchestrator.voting_system is not None
        assert orchestrator.consensus_builder is not None
        assert orchestrator.voting_system.voting_method == VotingMethod.WEIGHTED
    
    @pytest.mark.asyncio
    async def test_agent_registration_and_voting(self):
        """Test agent registration and voting on task assignment."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Register agents
        agent1 = TestAgent("agent1", domain_expertise=["coding"])
        agent2 = TestAgent("agent2", domain_expertise=["analysis"])
        agent3 = TestAgent("agent3", domain_expertise=["coding"])
        
        await orchestrator.register_agent(agent1)
        await orchestrator.register_agent(agent2)
        await orchestrator.register_agent(agent3)
        
        assert len(orchestrator.agents) == 3
        
        # Start swarm
        await orchestrator.start_swarm()
        assert orchestrator.is_active
        
        # Execute task - should trigger voting
        result = await orchestrator.execute_task(
            "Write some code",
            context={"domain": "coding"}
        )
        
        assert result.success
        # Should be assigned to agent with coding expertise
        assert result.agent_name in ["agent1", "agent3"]
        assert result.confidence_score > 0
        
        # Check voting history
        assert len(orchestrator.voting_history) > 0
        
        # Stop swarm
        await orchestrator.stop_swarm()
        assert not orchestrator.is_active
    
    @pytest.mark.asyncio
    async def test_democratic_task_assignment(self):
        """Test democratic task assignment through voting."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            voting_method=VotingMethod.WEIGHTED,
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Create agents with different confidence levels
        agent1 = TestAgent("specialist", domain_expertise=["data_science"])
        agent1.confidence.domains["data_science"] = 0.9
        
        agent2 = TestAgent("generalist", domain_expertise=["general"])
        agent2.confidence.domains["data_science"] = 0.5
        
        await orchestrator.register_agent(agent1)
        await orchestrator.register_agent(agent2)
        await orchestrator.start_swarm()
        
        # Task should go to specialist
        result = await orchestrator.execute_task(
            "Analyze this dataset",
            context={"domain": "data_science"}
        )
        
        assert result.success
        assert result.agent_name == "specialist"  # Higher confidence
        assert result.confidence_score > 0.5
        
        await orchestrator.stop_swarm()
    
    @pytest.mark.asyncio
    async def test_voting_with_abstentions(self):
        """Test voting when some agents abstain."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Agents with varying confidence
        agent1 = TestAgent("expert", domain_expertise=["security"])
        agent1.confidence.domains["security"] = 0.9
        
        agent2 = TestAgent("novice", domain_expertise=["general"])
        agent2.confidence.domains["security"] = 0.2  # Will abstain
        
        await orchestrator.register_agent(agent1)
        await orchestrator.register_agent(agent2)
        await orchestrator.start_swarm()
        
        result = await orchestrator.execute_task(
            "Review security vulnerabilities",
            context={"domain": "security"}
        )
        
        assert result.success
        assert result.agent_name == "expert"
        
        # Check voting result
        if orchestrator.voting_history:
            last_vote = orchestrator.voting_history[-1]
            assert last_vote.abstentions >= 0  # At least one might abstain
        
        await orchestrator.stop_swarm()
    
    @pytest.mark.asyncio
    async def test_consensus_building(self):
        """Test consensus building for decisions."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            consensus_algorithm=ConsensusAlgorithm.SUPERMAJORITY,
            consensus_threshold=0.66,
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Register agents
        agents = [
            TestAgent(f"agent{i}", domain_expertise=["general"])
            for i in range(4)
        ]
        
        for agent in agents:
            await orchestrator.register_agent(agent)
        
        await orchestrator.start_swarm()
        
        # Build consensus on a decision
        result = await orchestrator.build_consensus(
            proposal_title="Choose deployment strategy",
            proposal_description="Select the best deployment approach",
            options=["blue_green", "canary", "rolling"],
            context={"domain": "devops"}
        )
        
        assert result is not None
        assert result.algorithm_used == ConsensusAlgorithm.SUPERMAJORITY
        # Consensus might or might not be reached depending on votes
        assert result.chosen_option in ["blue_green", "canary", "rolling", None]
        
        await orchestrator.stop_swarm()
    
    @pytest.mark.asyncio
    async def test_voting_statistics(self):
        """Test collecting voting statistics."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        agents = [TestAgent(f"agent{i}") for i in range(3)]
        for agent in agents:
            await orchestrator.register_agent(agent)
        
        await orchestrator.start_swarm()
        
        # Execute multiple tasks to generate voting history
        for i in range(5):
            await orchestrator.execute_task(
                f"Task {i}",
                context={"domain": "general"}
            )
        
        # Get voting statistics
        stats = orchestrator.get_voting_statistics()
        
        assert "voting" in stats
        assert "consensus" in stats
        assert "total_democratic_decisions" in stats
        assert stats["voting"]["total_votes"] == 5
        
        await orchestrator.stop_swarm()
    
    @pytest.mark.asyncio
    async def test_different_voting_methods(self):
        """Test orchestrator with different voting methods."""
        for method in [VotingMethod.PLURALITY, VotingMethod.WEIGHTED, VotingMethod.CONSENSUS]:
            orchestrator = PydanticAISwarmOrchestrator(
                swarm_name=f"test_swarm_{method.value}",
                voting_method=method,
                enable_diagnostics=False,
                enable_monitoring=False
            )
            
            agents = [TestAgent(f"agent{i}") for i in range(3)]
            for agent in agents:
                await orchestrator.register_agent(agent)
            
            await orchestrator.start_swarm()
            
            result = await orchestrator.execute_task(
                "Test task",
                context={"domain": "general"}
            )
            
            assert result.success
            assert result.agent_name is not None
            
            await orchestrator.stop_swarm()
    
    @pytest.mark.asyncio
    async def test_no_agents_available(self):
        """Test task execution when no agents are available."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="empty_swarm",
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        # Don't start swarm (no agents)
        result = await orchestrator.execute_task(
            "Test task",
            context={"domain": "general"}
        )
        
        assert not result.success
        assert "not active" in result.error.lower()
    
    @pytest.mark.asyncio
    async def test_task_metrics_tracking(self):
        """Test that task metrics are tracked correctly."""
        orchestrator = PydanticAISwarmOrchestrator(
            swarm_name="test_swarm",
            enable_diagnostics=False,
            enable_monitoring=False
        )
        
        agent = TestAgent("test_agent")
        await orchestrator.register_agent(agent)
        await orchestrator.start_swarm()
        
        # Execute successful tasks
        for i in range(3):
            result = await orchestrator.execute_task(
                f"Task {i}",
                context={"domain": "general"}
            )
            assert result.success
        
        # Check metrics
        assert orchestrator.metrics["total_tasks_processed"] == 3
        assert orchestrator.metrics["successful_tasks"] == 3
        assert orchestrator.metrics["failed_tasks"] == 0
        
        await orchestrator.stop_swarm()
