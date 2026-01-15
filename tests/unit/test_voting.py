"""Tests for the voting system."""

import pytest
from datetime import datetime

from pydantic_ai_swarm.governance.voting import (
    VotingMethod,
    Vote,
    RankedVote,
    ApprovalVote,
    VotingResult,
    VotingSystem,
)


class TestVote:
    """Tests for Vote dataclass."""
    
    def test_vote_creation(self):
        """Test basic vote creation."""
        vote = Vote(
            agent_name="test_agent",
            option="option_a",
            weight=1.5,
            confidence=0.8
        )
        
        assert vote.agent_name == "test_agent"
        assert vote.option == "option_a"
        assert vote.weight == 1.5
        assert vote.confidence == 0.8
        assert not vote.abstain
    
    def test_vote_with_abstention(self):
        """Test vote with abstention."""
        vote = Vote(
            agent_name="test_agent",
            option="",
            abstain=True
        )
        
        assert vote.abstain
    
    def test_vote_validation_negative_weight(self):
        """Test that negative weight raises error."""
        with pytest.raises(ValueError, match="weight cannot be negative"):
            Vote(
                agent_name="test_agent",
                option="option_a",
                weight=-1.0
            )
    
    def test_vote_validation_confidence_bounds(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValueError, match="Confidence must be between 0 and 1"):
            Vote(
                agent_name="test_agent",
                option="option_a",
                confidence=1.5
            )


class TestRankedVote:
    """Tests for RankedVote."""
    
    def test_ranked_vote_creation(self):
        """Test ranked vote creation."""
        vote = RankedVote(
            agent_name="test_agent",
            option="option_a",
            rankings=["option_a", "option_b", "option_c"]
        )
        
        assert vote.rankings == ["option_a", "option_b", "option_c"]
    
    def test_ranked_vote_requires_rankings(self):
        """Test that rankings are required."""
        with pytest.raises(ValueError, match="Rankings must be provided"):
            RankedVote(
                agent_name="test_agent",
                option="option_a",
                rankings=[]
            )


class TestApprovalVote:
    """Tests for ApprovalVote."""
    
    def test_approval_vote_creation(self):
        """Test approval vote creation."""
        vote = ApprovalVote(
            agent_name="test_agent",
            option="option_a",
            approved_options={"option_a", "option_b"}
        )
        
        assert vote.approved_options == {"option_a", "option_b"}
    
    def test_approval_vote_requires_approvals(self):
        """Test that approvals are required."""
        with pytest.raises(ValueError, match="Must approve at least one option"):
            ApprovalVote(
                agent_name="test_agent",
                option="option_a",
                approved_options=set()
            )


class TestVotingSystem:
    """Tests for VotingSystem."""
    
    def test_voting_system_creation(self):
        """Test voting system creation."""
        system = VotingSystem(
            voting_method=VotingMethod.PLURALITY,
            consensus_threshold=0.66
        )
        
        assert system.voting_method == VotingMethod.PLURALITY
        assert system.consensus_threshold == 0.66
    
    def test_plurality_voting(self):
        """Test plurality voting mechanism."""
        system = VotingSystem(voting_method=VotingMethod.PLURALITY)
        
        votes = [
            Vote(agent_name="agent1", option="option_a", confidence=0.8),
            Vote(agent_name="agent2", option="option_a", confidence=0.7),
            Vote(agent_name="agent3", option="option_b", confidence=0.6),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        assert result.winner == "option_a"
        assert result.total_votes == 3
        assert result.abstentions == 0
        assert result.voting_method == VotingMethod.PLURALITY
    
    def test_weighted_voting(self):
        """Test weighted voting mechanism."""
        system = VotingSystem(voting_method=VotingMethod.WEIGHTED)
        
        votes = [
            Vote(agent_name="agent1", option="option_a", weight=1.0, confidence=0.8),
            Vote(agent_name="agent2", option="option_b", weight=2.0, confidence=0.9),
            Vote(agent_name="agent3", option="option_a", weight=0.5, confidence=0.6),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        # Option B should win due to higher weight and confidence
        assert result.winner == "option_b"
        assert result.voting_method == VotingMethod.WEIGHTED
    
    def test_voting_with_abstentions(self):
        """Test voting with some abstentions."""
        system = VotingSystem(voting_method=VotingMethod.PLURALITY)
        
        votes = [
            Vote(agent_name="agent1", option="option_a", confidence=0.8),
            Vote(agent_name="agent2", option="option_a", confidence=0.7),
            Vote(agent_name="agent3", option="", abstain=True),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        assert result.winner == "option_a"
        assert result.abstentions == 1
        assert result.participation_rate == 1.0  # All voted (some abstained)
    
    def test_ranked_choice_voting(self):
        """Test ranked-choice voting."""
        system = VotingSystem(voting_method=VotingMethod.RANKED_CHOICE)
        
        votes = [
            RankedVote(
                agent_name="agent1",
                option="option_a",
                rankings=["option_a", "option_b", "option_c"]
            ),
            RankedVote(
                agent_name="agent2",
                option="option_b",
                rankings=["option_b", "option_a", "option_c"]
            ),
            RankedVote(
                agent_name="agent3",
                option="option_c",
                rankings=["option_c", "option_a", "option_b"]
            ),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        # One of the options should win
        assert result.winner in ["option_a", "option_b", "option_c"]
        assert result.voting_method == VotingMethod.RANKED_CHOICE
    
    def test_approval_voting(self):
        """Test approval voting."""
        system = VotingSystem(voting_method=VotingMethod.APPROVAL)
        
        votes = [
            ApprovalVote(
                agent_name="agent1",
                option="option_a",
                approved_options={"option_a", "option_b"}
            ),
            ApprovalVote(
                agent_name="agent2",
                option="option_b",
                approved_options={"option_b", "option_c"}
            ),
            ApprovalVote(
                agent_name="agent3",
                option="option_b",
                approved_options={"option_a", "option_b"}
            ),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        # Option B should have most approvals
        assert result.winner == "option_b"
        assert result.voting_method == VotingMethod.APPROVAL
    
    def test_consensus_voting_success(self):
        """Test consensus voting when threshold is met."""
        system = VotingSystem(
            voting_method=VotingMethod.CONSENSUS,
            consensus_threshold=0.66
        )
        
        votes = [
            Vote(agent_name="agent1", option="option_a", weight=1.0, confidence=0.9),
            Vote(agent_name="agent2", option="option_a", weight=1.0, confidence=0.8),
            Vote(agent_name="agent3", option="option_b", weight=1.0, confidence=0.7),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        # Should reach consensus on option_a (2/3 = 66.7%)
        assert result.winner == "option_a"
        assert result.consensus_level >= 0.66
    
    def test_consensus_voting_failure(self):
        """Test consensus voting when threshold is not met."""
        system = VotingSystem(
            voting_method=VotingMethod.CONSENSUS,
            consensus_threshold=0.9  # Very high threshold
        )
        
        votes = [
            Vote(agent_name="agent1", option="option_a", weight=1.0, confidence=0.8),
            Vote(agent_name="agent2", option="option_b", weight=1.0, confidence=0.7),
            Vote(agent_name="agent3", option="option_c", weight=1.0, confidence=0.6),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        # Should not reach consensus (votes are split)
        assert result.winner is None
        assert result.consensus_level < 0.9
    
    def test_low_participation(self):
        """Test handling of low participation."""
        system = VotingSystem(
            voting_method=VotingMethod.PLURALITY,
            min_participation=0.5
        )
        
        votes = [
            Vote(agent_name="agent1", option="option_a", confidence=0.8),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=10)
        
        # Participation is 10%, below minimum of 50%
        assert result.participation_rate == 0.1
        assert result.winner == "option_a"  # Still has a winner
    
    def test_voting_result_confidence(self):
        """Test calculating winner confidence."""
        system = VotingSystem(voting_method=VotingMethod.WEIGHTED)
        
        votes = [
            Vote(agent_name="agent1", option="option_a", weight=2.0, confidence=0.9),
            Vote(agent_name="agent2", option="option_a", weight=1.5, confidence=0.8),
            Vote(agent_name="agent3", option="option_b", weight=1.0, confidence=0.7),
        ]
        
        result = system.conduct_vote(votes, eligible_voters=3)
        
        assert result.winner == "option_a"
        winner_confidence = result.get_winner_confidence()
        assert 0 <= winner_confidence <= 1
        assert winner_confidence > 0.5  # Should be reasonably high
    
    def test_voting_statistics(self):
        """Test collecting voting statistics."""
        system = VotingSystem(voting_method=VotingMethod.PLURALITY)
        
        # Conduct multiple votes
        for i in range(5):
            votes = [
                Vote(agent_name="agent1", option="option_a", confidence=0.8),
                Vote(agent_name="agent2", option="option_b", confidence=0.7),
            ]
            system.conduct_vote(votes, eligible_voters=2)
        
        stats = system.get_voting_statistics()
        
        assert stats["total_votes"] == 5
        assert "average_consensus" in stats
        assert "average_participation" in stats
        assert "method_distribution" in stats
        assert stats["method_distribution"]["plurality"] == 5
