"""Democratic Voting Mechanisms for Agent Swarm.

This module implements various voting mechanisms for democratic decision-making
in the agent swarm, including plurality voting, ranked-choice voting, and
approval voting.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import logging


logger = logging.getLogger(__name__)


class VotingMethod(Enum):
    """Supported voting methods."""
    PLURALITY = "plurality"  # Simple majority
    WEIGHTED = "weighted"  # Confidence-weighted votes
    RANKED_CHOICE = "ranked_choice"  # Ranked preference voting
    APPROVAL = "approval"  # Approve/disapprove multiple options
    CONSENSUS = "consensus"  # Require high agreement threshold


@dataclass
class Vote:
    """Represents a single vote from an agent."""
    agent_name: str
    option: str
    weight: float = 1.0
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    abstain: bool = False
    reasoning: str = ""
    context_confidence: float = 0.5
    
    def __post_init__(self):
        """Validate vote data."""
        if self.weight < 0:
            raise ValueError("Vote weight cannot be negative")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class RankedVote(Vote):
    """Represents a ranked-choice vote."""
    rankings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate ranked vote data."""
        super().__post_init__()
        if not self.rankings and not self.abstain:
            raise ValueError("Rankings must be provided for ranked-choice voting")


@dataclass
class ApprovalVote(Vote):
    """Represents an approval vote (can approve multiple options)."""
    approved_options: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        """Validate approval vote data."""
        super().__post_init__()
        if not self.approved_options and not self.abstain:
            raise ValueError("Must approve at least one option")


@dataclass
class VotingResult:
    """Results of a voting session."""
    winner: Optional[str]
    vote_counts: Dict[str, float]
    total_votes: int
    abstentions: int
    voting_method: VotingMethod
    consensus_level: float
    participation_rate: float
    all_votes: List[Vote] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_winner_confidence(self) -> float:
        """Calculate confidence in the winning option."""
        if not self.winner or not self.vote_counts:
            return 0.0
        
        winner_votes = self.vote_counts.get(self.winner, 0)
        total_votes_cast = sum(self.vote_counts.values())
        
        if total_votes_cast == 0:
            return 0.0
        
        # Confidence based on vote proportion and consensus level
        vote_proportion = winner_votes / total_votes_cast
        confidence = (vote_proportion * 0.7) + (self.consensus_level * 0.3)
        
        # Ensure confidence is clamped to [0, 1]
        return max(0.0, min(1.0, confidence))


class VotingSystem:
    """Democratic voting system for agent swarm decisions."""
    
    def __init__(
        self,
        voting_method: VotingMethod = VotingMethod.WEIGHTED,
        consensus_threshold: float = 0.66,
        min_participation: float = 0.5
    ):
        """Initialize voting system.
        
        Args:
            voting_method: Default voting method to use
            consensus_threshold: Minimum agreement level for consensus
            min_participation: Minimum participation rate required
        """
        self.voting_method = voting_method
        self.consensus_threshold = consensus_threshold
        self.min_participation = min_participation
        self.voting_history: List[VotingResult] = []
        
    def conduct_vote(
        self,
        votes: List[Vote],
        eligible_voters: int,
        method: Optional[VotingMethod] = None
    ) -> VotingResult:
        """Conduct a vote using the specified method.
        
        Args:
            votes: List of votes cast
            eligible_voters: Total number of eligible voters
            method: Voting method to use (defaults to system default)
            
        Returns:
            VotingResult with winner and vote analysis
        """
        method = method or self.voting_method
        
        # Filter out abstentions
        active_votes = [v for v in votes if not v.abstain]
        abstentions = len(votes) - len(active_votes)
        
        # Calculate participation rate
        participation_rate = len(votes) / eligible_voters if eligible_voters > 0 else 0
        
        # Check minimum participation
        if participation_rate < self.min_participation:
            logger.warning(
                f"Participation rate {participation_rate:.2%} below minimum "
                f"{self.min_participation:.2%}"
            )
        
        # Execute voting method
        if method == VotingMethod.PLURALITY:
            vote_counts, winner = self._plurality_vote(active_votes)
        elif method == VotingMethod.WEIGHTED:
            vote_counts, winner = self._weighted_vote(active_votes)
        elif method == VotingMethod.RANKED_CHOICE:
            vote_counts, winner = self._ranked_choice_vote(active_votes)
        elif method == VotingMethod.APPROVAL:
            vote_counts, winner = self._approval_vote(active_votes)
        elif method == VotingMethod.CONSENSUS:
            vote_counts, winner = self._consensus_vote(active_votes)
        else:
            raise ValueError(f"Unsupported voting method: {method}")
        
        # Calculate consensus level
        consensus_level = self._calculate_consensus(vote_counts, active_votes)
        
        # Create result
        result = VotingResult(
            winner=winner,
            vote_counts=vote_counts,
            total_votes=len(votes),
            abstentions=abstentions,
            voting_method=method,
            consensus_level=consensus_level,
            participation_rate=participation_rate,
            all_votes=votes,
            metadata={
                "eligible_voters": eligible_voters,
                "threshold_met": consensus_level >= self.consensus_threshold
            }
        )
        
        # Store in history
        self.voting_history.append(result)
        
        logger.info(
            f"Vote completed: {method.value} - Winner: {winner} "
            f"(consensus: {consensus_level:.2%})"
        )
        
        return result
    
    def _plurality_vote(self, votes: List[Vote]) -> tuple[Dict[str, float], Optional[str]]:
        """Simple plurality voting - one vote per agent, most votes wins.
        
        Args:
            votes: List of active votes
            
        Returns:
            Tuple of (vote_counts, winner)
        """
        vote_counts: Dict[str, float] = {}
        
        for vote in votes:
            vote_counts[vote.option] = vote_counts.get(vote.option, 0) + 1
        
        if not vote_counts:
            return {}, None
        
        winner = max(vote_counts.items(), key=lambda x: x[1])[0]
        return vote_counts, winner
    
    def _weighted_vote(self, votes: List[Vote]) -> tuple[Dict[str, float], Optional[str]]:
        """Confidence-weighted voting - votes weighted by agent confidence.
        
        Args:
            votes: List of active votes
            
        Returns:
            Tuple of (vote_counts, winner)
        """
        vote_counts: Dict[str, float] = {}
        
        for vote in votes:
            # Weight combines vote weight and confidence
            effective_weight = vote.weight * (0.5 + vote.confidence * 0.5)
            vote_counts[vote.option] = vote_counts.get(vote.option, 0) + effective_weight
        
        if not vote_counts:
            return {}, None
        
        winner = max(vote_counts.items(), key=lambda x: x[1])[0]
        return vote_counts, winner
    
    def _ranked_choice_vote(self, votes: List[Vote]) -> tuple[Dict[str, float], Optional[str]]:
        """Ranked-choice (instant runoff) voting.
        
        Args:
            votes: List of active votes (must be RankedVote instances)
            
        Returns:
            Tuple of (vote_counts, winner)
        """
        if not votes:
            return {}, None
        
        # Convert to ranked votes if needed
        ranked_votes = []
        for vote in votes:
            if isinstance(vote, RankedVote):
                ranked_votes.append(vote)
            else:
                # Convert regular vote to ranked vote with single ranking
                ranked_vote = RankedVote(
                    agent_name=vote.agent_name,
                    option=vote.option,
                    weight=vote.weight,
                    confidence=vote.confidence,
                    rankings=[vote.option]
                )
                ranked_votes.append(ranked_vote)
        
        # Collect all candidates
        all_candidates = set()
        for vote in ranked_votes:
            all_candidates.update(vote.rankings)
        
        remaining_candidates = list(all_candidates)
        vote_counts: Dict[str, float] = {c: 0.0 for c in remaining_candidates}
        
        # Instant runoff rounds
        while len(remaining_candidates) > 1:
            # Count first-choice votes
            round_counts: Dict[str, float] = {c: 0.0 for c in remaining_candidates}
            
            for vote in ranked_votes:
                # Find first remaining candidate in rankings
                for candidate in vote.rankings:
                    if candidate in remaining_candidates:
                        round_counts[candidate] += vote.weight
                        break
            
            # Check if any candidate has majority
            total_votes = sum(round_counts.values())
            for candidate, count in round_counts.items():
                if total_votes > 0 and count / total_votes > 0.5:
                    vote_counts.update(round_counts)
                    return vote_counts, candidate
            
            # Eliminate candidate with fewest votes
            if round_counts:
                loser = min(round_counts.items(), key=lambda x: x[1])[0]
                remaining_candidates.remove(loser)
                vote_counts.update(round_counts)
            else:
                break
        
        # Return last remaining candidate
        winner = remaining_candidates[0] if remaining_candidates else None
        return vote_counts, winner
    
    def _approval_vote(self, votes: List[Vote]) -> tuple[Dict[str, float], Optional[str]]:
        """Approval voting - agents can approve multiple options.
        
        Args:
            votes: List of active votes (must be ApprovalVote instances)
            
        Returns:
            Tuple of (vote_counts, winner)
        """
        vote_counts: Dict[str, float] = {}
        
        for vote in votes:
            if isinstance(vote, ApprovalVote):
                # Count approvals with confidence weighting
                for option in vote.approved_options:
                    weight = vote.weight * (0.5 + vote.confidence * 0.5)
                    vote_counts[option] = vote_counts.get(option, 0) + weight
            else:
                # Treat regular vote as single approval
                weight = vote.weight * (0.5 + vote.confidence * 0.5)
                vote_counts[vote.option] = vote_counts.get(vote.option, 0) + weight
        
        if not vote_counts:
            return {}, None
        
        winner = max(vote_counts.items(), key=lambda x: x[1])[0]
        return vote_counts, winner
    
    def _consensus_vote(self, votes: List[Vote]) -> tuple[Dict[str, float], Optional[str]]:
        """Consensus voting - requires high agreement threshold.
        
        Args:
            votes: List of active votes
            
        Returns:
            Tuple of (vote_counts, winner) or (counts, None) if no consensus
        """
        vote_counts: Dict[str, float] = {}
        total_weight = 0.0
        
        for vote in votes:
            weight = vote.weight * (0.5 + vote.confidence * 0.5)
            vote_counts[vote.option] = vote_counts.get(vote.option, 0) + weight
            total_weight += weight
        
        if not vote_counts or total_weight == 0:
            return {}, None
        
        # Find option with highest votes
        top_option, top_votes = max(vote_counts.items(), key=lambda x: x[1])
        
        # Check if it meets consensus threshold
        if top_votes / total_weight >= self.consensus_threshold:
            return vote_counts, top_option
        else:
            logger.warning(
                f"Consensus threshold {self.consensus_threshold:.2%} not met. "
                f"Top option only has {top_votes/total_weight:.2%} support."
            )
            return vote_counts, None
    
    def _calculate_consensus(
        self,
        vote_counts: Dict[str, float],
        votes: List[Vote]
    ) -> float:
        """Calculate consensus level for the vote.
        
        Args:
            vote_counts: Vote tallies by option
            votes: List of votes cast
            
        Returns:
            Consensus level (0-1)
        """
        if not vote_counts or not votes:
            return 0.0
        
        total_weight = sum(vote_counts.values())
        if total_weight == 0:
            return 0.0
        
        # Get top option's proportion
        top_votes = max(vote_counts.values())
        top_proportion = top_votes / total_weight
        
        # Consider vote concentration (higher consensus if fewer options)
        option_diversity = len(vote_counts)
        diversity_factor = 1.0 / max(1, option_diversity - 1)
        
        # Consensus is blend of top proportion and diversity
        consensus = (top_proportion * 0.7) + (diversity_factor * 0.3)
        
        return min(1.0, consensus)
    
    def get_voting_statistics(self) -> Dict[str, Any]:
        """Get statistics about voting history.
        
        Returns:
            Dictionary with voting statistics
        """
        if not self.voting_history:
            return {
                "total_votes": 0,
                "average_consensus": 0.0,
                "average_participation": 0.0,
                "method_distribution": {}
            }
        
        total_votes = len(self.voting_history)
        avg_consensus = sum(v.consensus_level for v in self.voting_history) / total_votes
        avg_participation = sum(v.participation_rate for v in self.voting_history) / total_votes
        
        # Count voting methods used
        method_counts: Dict[str, int] = {}
        for result in self.voting_history:
            method_name = result.voting_method.value
            method_counts[method_name] = method_counts.get(method_name, 0) + 1
        
        return {
            "total_votes": total_votes,
            "average_consensus": avg_consensus,
            "average_participation": avg_participation,
            "method_distribution": method_counts,
            "recent_winners": [v.winner for v in self.voting_history[-10:]]
        }
