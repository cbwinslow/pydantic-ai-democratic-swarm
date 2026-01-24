"""Tests for the consensus building system."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from pydantic_ai_swarm.governance.consensus import (
    ConsensusAlgorithm,
    ConsensusProposal,
    ConsensusRound,
    ConsensusResult,
    ConsensusBuilder,
)


class MockAgent:
    """Mock agent for testing."""
    
    def __init__(self, name: str, confidence: float = 0.8, preferred_option: str = "option_a"):
        """Initialize mock agent.
        
        Args:
            name: Agent name
            confidence: Default confidence level
            preferred_option: Preferred option to vote for
        """
        self.agent_name = name
        self.default_confidence = confidence
        self.preferred_option = preferred_option
        self.confidence = MagicMock()
        self.confidence.get_domain_confidence = MagicMock(return_value=confidence)
    
    def should_abstain_from_vote(self, domain: str) -> bool:
        """Check if agent should abstain."""
        return self.default_confidence < 0.3
    
    async def calculate_task_confidence(self, task: str, context: dict) -> float:
        """Calculate task confidence.
        
        Returns higher confidence for preferred option.
        """
        # Check if this task mentions the preferred option
        if self.preferred_option in task:
            return self.default_confidence
        else:
            # Return lower confidence for other options
            return self.default_confidence * 0.5
    
    def get_voting_weight(self, domain: str = "") -> float:
        """Get voting weight."""
        return self.default_confidence


class TestConsensusProposal:
    """Tests for ConsensusProposal."""
    
    def test_proposal_creation(self):
        """Test basic proposal creation."""
        proposal = ConsensusProposal(
            proposal_id="test_001",
            title="Test Proposal",
            description="Choose the best option",
            options=["option_a", "option_b", "option_c"],
            proposer="orchestrator"
        )
        
        assert proposal.proposal_id == "test_001"
        assert proposal.title == "Test Proposal"
        assert len(proposal.options) == 3
        assert proposal.proposer == "orchestrator"
    
    def test_proposal_requires_options(self):
        """Test that proposal must have options."""
        with pytest.raises(ValueError, match="must have at least one option"):
            ConsensusProposal(
                proposal_id="test_001",
                title="Test",
                description="Test",
                options=[],
                proposer="test"
            )
    
    def test_proposal_requires_id(self):
        """Test that proposal must have an ID."""
        with pytest.raises(ValueError, match="must have an ID"):
            ConsensusProposal(
                proposal_id="",
                title="Test",
                description="Test",
                options=["option_a"],
                proposer="test"
            )


class TestConsensusBuilder:
    """Tests for ConsensusBuilder."""
    
    def test_consensus_builder_creation(self):
        """Test consensus builder initialization."""
        builder = ConsensusBuilder(
            algorithm=ConsensusAlgorithm.SUPERMAJORITY,
            agreement_threshold=0.66,
            quorum=0.5
        )
        
        assert builder.algorithm == ConsensusAlgorithm.SUPERMAJORITY
        assert builder.agreement_threshold == 0.66
        assert builder.quorum == 0.5
    
    @pytest.mark.asyncio
    async def test_simple_majority_consensus(self):
        """Test simple majority consensus."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.SIMPLE_MAJORITY)
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.7, preferred_option="option_a"),
            MockAgent("agent3", confidence=0.6, preferred_option="option_b"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_001",
            title="Test Decision",
            description="Choose option",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        assert result.consensus_reached is True
        assert result.chosen_option == "option_a"  # 2 out of 3
        assert result.algorithm_used == ConsensusAlgorithm.SIMPLE_MAJORITY
    
    @pytest.mark.asyncio
    async def test_supermajority_consensus_success(self):
        """Test supermajority consensus when threshold is met."""
        builder = ConsensusBuilder(
            algorithm=ConsensusAlgorithm.SUPERMAJORITY,
            agreement_threshold=0.66
        )
        
        agents = [
            MockAgent("agent1", confidence=0.9, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent3", confidence=0.7, preferred_option="option_b"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_002",
            title="Important Decision",
            description="Choose option with supermajority",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        assert result.consensus_reached is True
        assert result.chosen_option == "option_a"
        assert result.agreement_level >= 0.66
    
    @pytest.mark.asyncio
    async def test_supermajority_consensus_failure(self):
        """Test supermajority when threshold is not met."""
        builder = ConsensusBuilder(
            algorithm=ConsensusAlgorithm.SUPERMAJORITY,
            agreement_threshold=0.9  # Very high threshold
        )
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.7, preferred_option="option_b"),
            MockAgent("agent3", confidence=0.6, preferred_option="option_c"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_003",
            title="Difficult Decision",
            description="Try to reach consensus",
            options=["option_a", "option_b", "option_c"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        # Might not reach consensus due to split votes
        assert result.agreement_level < 0.9
    
    @pytest.mark.asyncio
    async def test_unanimous_consensus(self):
        """Test unanimous consensus requirement."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.UNANIMOUS)
        
        # All agents agree
        agents = [
            MockAgent("agent1", confidence=0.9, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent3", confidence=0.7, preferred_option="option_a"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_004",
            title="Critical Decision",
            description="Requires unanimous agreement",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        assert result.consensus_reached is True
        assert result.chosen_option == "option_a"
        assert result.agreement_level >= 0.99
    
    @pytest.mark.asyncio
    async def test_quorum_based_consensus(self):
        """Test quorum-based consensus."""
        builder = ConsensusBuilder(
            algorithm=ConsensusAlgorithm.QUORUM_BASED,
            quorum=0.5  # Need at least 50% participation
        )
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.7, preferred_option="option_a"),
            MockAgent("agent3", confidence=0.1, preferred_option="option_b"),  # Will abstain
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_005",
            title="Quorum Decision",
            description="Need quorum to decide",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        # Should still reach consensus with 2/3 participation
        assert result.consensus_reached is True
        assert result.chosen_option == "option_a"
        assert "quorum_met" in result.metadata
    
    @pytest.mark.asyncio
    async def test_iterative_refinement(self):
        """Test iterative refinement consensus building."""
        builder = ConsensusBuilder(
            algorithm=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
            agreement_threshold=0.66,
            max_rounds=3
        )
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.7, preferred_option="option_a"),
            MockAgent("agent3", confidence=0.6, preferred_option="option_b"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_006",
            title="Iterative Decision",
            description="Build consensus through multiple rounds",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        assert len(result.rounds) >= 1
        assert result.algorithm_used == ConsensusAlgorithm.ITERATIVE_REFINEMENT
        # May reach consensus in first round
        assert result.chosen_option in ["option_a", "option_b"]
    
    @pytest.mark.asyncio
    async def test_delegated_consensus(self):
        """Test delegated consensus (high-confidence agents decide)."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.DELEGATED)
        
        agents = [
            MockAgent("agent1", confidence=0.9, preferred_option="option_a"),  # High confidence
            MockAgent("agent2", confidence=0.8, preferred_option="option_a"),  # High confidence
            MockAgent("agent3", confidence=0.4, preferred_option="option_b"),  # Low confidence
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_007",
            title="Expert Decision",
            description="Delegate to high-confidence agents",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        # High-confidence agents should determine outcome
        assert result.consensus_reached is True
        assert result.chosen_option == "option_a"
        assert "high_confidence_voters" in result.metadata
    
    @pytest.mark.asyncio
    async def test_consensus_with_abstentions(self):
        """Test consensus building with agent abstentions."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.SIMPLE_MAJORITY)
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.2, preferred_option="option_a"),  # Will abstain
            MockAgent("agent3", confidence=0.7, preferred_option="option_b"),
        ]
        
        proposal = ConsensusProposal(
            proposal_id="test_008",
            title="Decision with Abstentions",
            description="Some agents abstain",
            options=["option_a", "option_b"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, agents)
        
        # Should still work with abstentions
        assert result.algorithm_used == ConsensusAlgorithm.SIMPLE_MAJORITY
        assert result.chosen_option in ["option_a", "option_b"]
    
    @pytest.mark.asyncio
    async def test_consensus_statistics(self):
        """Test collecting consensus statistics."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.SIMPLE_MAJORITY)
        
        agents = [
            MockAgent("agent1", confidence=0.8, preferred_option="option_a"),
            MockAgent("agent2", confidence=0.7, preferred_option="option_a"),
        ]
        
        # Run multiple consensus rounds
        for i in range(3):
            proposal = ConsensusProposal(
                proposal_id=f"test_{i}",
                title=f"Decision {i}",
                description="Test decision",
                options=["option_a", "option_b"],
                proposer="orchestrator"
            )
            
            await builder.build_consensus(proposal, agents)
        
        stats = builder.get_consensus_statistics()
        
        assert stats["total_proposals"] == 3
        assert "consensus_rate" in stats
        assert "average_agreement" in stats
        assert "average_rounds" in stats
        assert len(stats["recent_results"]) == 3
    
    @pytest.mark.asyncio
    async def test_no_agents(self):
        """Test consensus building with no agents."""
        builder = ConsensusBuilder(algorithm=ConsensusAlgorithm.SIMPLE_MAJORITY)
        
        proposal = ConsensusProposal(
            proposal_id="test_empty",
            title="No Agents",
            description="Consensus with no agents",
            options=["option_a"],
            proposer="orchestrator"
        )
        
        result = await builder.build_consensus(proposal, [])
        
        # Should handle gracefully
        assert result.consensus_reached is False
        assert result.chosen_option is None
