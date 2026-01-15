"""Consensus Building Algorithms for Democratic Decision-Making.

This module implements various consensus-building algorithms that help
the swarm reach agreement on decisions through iterative refinement
and collaborative deliberation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
import logging
import asyncio


logger = logging.getLogger(__name__)


class ConsensusAlgorithm(Enum):
    """Available consensus algorithms."""
    SIMPLE_MAJORITY = "simple_majority"  # >50% agreement
    SUPERMAJORITY = "supermajority"  # >66% agreement
    UNANIMOUS = "unanimous"  # 100% agreement
    QUORUM_BASED = "quorum_based"  # Minimum participation + majority
    ITERATIVE_REFINEMENT = "iterative_refinement"  # Multiple rounds to build consensus
    DELEGATED = "delegated"  # Delegate to high-confidence agents


@dataclass
class ConsensusProposal:
    """A proposal for the swarm to reach consensus on."""
    proposal_id: str
    title: str
    description: str
    options: List[str]
    proposer: str
    created_at: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate proposal."""
        if not self.options:
            raise ValueError("Proposal must have at least one option")
        if not self.proposal_id:
            raise ValueError("Proposal must have an ID")


@dataclass
class ConsensusRound:
    """Represents one round of consensus building."""
    round_number: int
    votes: Dict[str, Any]  # agent_name -> vote
    agreement_level: float
    timestamp: datetime = field(default_factory=datetime.now)
    feedback: Dict[str, str] = field(default_factory=dict)  # agent_name -> feedback


@dataclass
class ConsensusResult:
    """Result of a consensus-building process."""
    proposal_id: str
    consensus_reached: bool
    chosen_option: Optional[str]
    agreement_level: float
    rounds: List[ConsensusRound]
    participating_agents: Set[str]
    algorithm_used: ConsensusAlgorithm
    duration_seconds: float
    final_votes: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsensusBuilder:
    """Builds consensus among agents using various algorithms."""
    
    def __init__(
        self,
        algorithm: ConsensusAlgorithm = ConsensusAlgorithm.SUPERMAJORITY,
        agreement_threshold: float = 0.66,
        quorum: float = 0.5,
        max_rounds: int = 3,
        round_timeout_seconds: float = 60.0
    ):
        """Initialize consensus builder.
        
        Args:
            algorithm: Default consensus algorithm
            agreement_threshold: Minimum agreement level (0-1)
            quorum: Minimum participation rate (0-1)
            max_rounds: Maximum rounds for iterative algorithms
            round_timeout_seconds: Timeout for each round
        """
        self.algorithm = algorithm
        self.agreement_threshold = agreement_threshold
        self.quorum = quorum
        self.max_rounds = max_rounds
        self.round_timeout_seconds = round_timeout_seconds
        self.consensus_history: List[ConsensusResult] = []
        
    async def build_consensus(
        self,
        proposal: ConsensusProposal,
        agents: List[Any],  # List of agent objects
        algorithm: Optional[ConsensusAlgorithm] = None
    ) -> ConsensusResult:
        """Build consensus on a proposal.
        
        Args:
            proposal: The proposal to decide on
            agents: List of agents who will participate
            algorithm: Algorithm to use (defaults to instance algorithm)
            
        Returns:
            ConsensusResult with decision and metadata
        """
        algorithm = algorithm or self.algorithm
        start_time = datetime.now()
        
        logger.info(
            f"Starting consensus on proposal '{proposal.title}' "
            f"with {len(agents)} agents using {algorithm.value}"
        )
        
        # Execute appropriate algorithm
        if algorithm == ConsensusAlgorithm.SIMPLE_MAJORITY:
            result = await self._simple_majority(proposal, agents)
        elif algorithm == ConsensusAlgorithm.SUPERMAJORITY:
            result = await self._supermajority(proposal, agents)
        elif algorithm == ConsensusAlgorithm.UNANIMOUS:
            result = await self._unanimous(proposal, agents)
        elif algorithm == ConsensusAlgorithm.QUORUM_BASED:
            result = await self._quorum_based(proposal, agents)
        elif algorithm == ConsensusAlgorithm.ITERATIVE_REFINEMENT:
            result = await self._iterative_refinement(proposal, agents)
        elif algorithm == ConsensusAlgorithm.DELEGATED:
            result = await self._delegated(proposal, agents)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        result.duration_seconds = duration
        
        # Store in history
        self.consensus_history.append(result)
        
        logger.info(
            f"Consensus {'reached' if result.consensus_reached else 'not reached'}: "
            f"{result.chosen_option} (agreement: {result.agreement_level:.2%})"
        )
        
        return result
    
    async def _collect_votes(
        self,
        proposal: ConsensusProposal,
        agents: List[Any],
        round_number: int = 1
    ) -> tuple[Dict[str, Any], Set[str]]:
        """Collect votes from agents.
        
        Args:
            proposal: The proposal to vote on
            agents: List of agents
            round_number: Current round number
            
        Returns:
            Tuple of (votes dict, participating agents set)
        """
        votes: Dict[str, Any] = {}
        participating_agents: Set[str] = set()
        
        # Collect votes with timeout
        vote_tasks = []
        for agent in agents:
            task = asyncio.create_task(
                self._get_agent_vote(agent, proposal, round_number)
            )
            vote_tasks.append((agent.agent_name, task))
        
        # Wait for all votes with timeout
        for agent_name, task in vote_tasks:
            try:
                vote = await asyncio.wait_for(task, timeout=self.round_timeout_seconds)
                if vote is not None:
                    votes[agent_name] = vote
                    participating_agents.add(agent_name)
            except asyncio.TimeoutError:
                logger.warning(f"Agent {agent_name} vote timed out")
            except Exception as e:
                logger.error(f"Error getting vote from {agent_name}: {e}")
        
        return votes, participating_agents
    
    async def _get_agent_vote(
        self,
        agent: Any,
        proposal: ConsensusProposal,
        round_number: int
    ) -> Optional[Dict[str, Any]]:
        """Get a vote from a single agent.
        
        Args:
            agent: Agent to get vote from
            proposal: The proposal
            round_number: Current round number
            
        Returns:
            Vote dictionary or None if abstaining
        """
        try:
            # Check if agent should abstain
            should_abstain = await agent.should_abstain_from_vote(
                proposal.context.get("domain", "")
            )
            
            if should_abstain:
                return None
            
            # Calculate confidence for each option
            option_confidences = {}
            for option in proposal.options:
                confidence = await agent.calculate_task_confidence(
                    f"{proposal.description}: {option}",
                    proposal.context
                )
                option_confidences[option] = confidence
            
            # Choose option with highest confidence
            best_option = max(option_confidences.items(), key=lambda x: x[1])
            
            return {
                "option": best_option[0],
                "confidence": best_option[1],
                "weight": agent.get_voting_weight(proposal.context.get("domain", "")),
                "round": round_number
            }
            
        except Exception as e:
            logger.error(f"Error getting vote from {agent.agent_name}: {e}")
            return None
    
    def _calculate_agreement_level(
        self,
        votes: Dict[str, Any],
        total_eligible: int
    ) -> float:
        """Calculate the level of agreement in votes.
        
        Args:
            votes: Dictionary of votes
            total_eligible: Total number of eligible voters
            
        Returns:
            Agreement level (0-1)
        """
        if not votes or total_eligible == 0:
            return 0.0
        
        # Count votes for each option
        option_counts: Dict[str, float] = {}
        total_weight = 0.0
        
        for vote in votes.values():
            option = vote.get("option")
            weight = vote.get("weight", 1.0)
            confidence = vote.get("confidence", 0.5)
            
            # Effective weight combines weight and confidence
            effective_weight = weight * (0.5 + confidence * 0.5)
            option_counts[option] = option_counts.get(option, 0) + effective_weight
            total_weight += effective_weight
        
        if total_weight == 0:
            return 0.0
        
        # Agreement is proportion of votes for top option
        top_votes = max(option_counts.values())
        agreement = top_votes / total_weight
        
        return agreement
    
    def _get_winning_option(self, votes: Dict[str, Any]) -> Optional[str]:
        """Determine winning option from votes.
        
        Args:
            votes: Dictionary of votes
            
        Returns:
            Winning option or None
        """
        if not votes:
            return None
        
        # Count weighted votes
        option_counts: Dict[str, float] = {}
        
        for vote in votes.values():
            option = vote.get("option")
            weight = vote.get("weight", 1.0)
            confidence = vote.get("confidence", 0.5)
            
            effective_weight = weight * (0.5 + confidence * 0.5)
            option_counts[option] = option_counts.get(option, 0) + effective_weight
        
        if not option_counts:
            return None
        
        return max(option_counts.items(), key=lambda x: x[1])[0]
    
    async def _simple_majority(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Simple majority (>50%) consensus.
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        votes, participating = await self._collect_votes(proposal, agents)
        agreement = self._calculate_agreement_level(votes, len(agents))
        winner = self._get_winning_option(votes)
        
        consensus_reached = agreement > 0.5 and len(participating) >= len(agents) * self.quorum
        
        round_data = ConsensusRound(
            round_number=1,
            votes=votes,
            agreement_level=agreement
        )
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=consensus_reached,
            chosen_option=winner if consensus_reached else None,
            agreement_level=agreement,
            rounds=[round_data],
            participating_agents=participating,
            algorithm_used=ConsensusAlgorithm.SIMPLE_MAJORITY,
            duration_seconds=0.0,
            final_votes=votes
        )
    
    async def _supermajority(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Supermajority (>66%) consensus.
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        votes, participating = await self._collect_votes(proposal, agents)
        agreement = self._calculate_agreement_level(votes, len(agents))
        winner = self._get_winning_option(votes)
        
        consensus_reached = (
            agreement >= self.agreement_threshold and
            len(participating) >= len(agents) * self.quorum
        )
        
        round_data = ConsensusRound(
            round_number=1,
            votes=votes,
            agreement_level=agreement
        )
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=consensus_reached,
            chosen_option=winner if consensus_reached else None,
            agreement_level=agreement,
            rounds=[round_data],
            participating_agents=participating,
            algorithm_used=ConsensusAlgorithm.SUPERMAJORITY,
            duration_seconds=0.0,
            final_votes=votes
        )
    
    async def _unanimous(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Unanimous (100%) consensus.
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        votes, participating = await self._collect_votes(proposal, agents)
        agreement = self._calculate_agreement_level(votes, len(agents))
        winner = self._get_winning_option(votes)
        
        # Unanimous requires all participating agents to agree
        consensus_reached = agreement >= 0.99 and len(participating) >= len(agents) * self.quorum
        
        round_data = ConsensusRound(
            round_number=1,
            votes=votes,
            agreement_level=agreement
        )
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=consensus_reached,
            chosen_option=winner if consensus_reached else None,
            agreement_level=agreement,
            rounds=[round_data],
            participating_agents=participating,
            algorithm_used=ConsensusAlgorithm.UNANIMOUS,
            duration_seconds=0.0,
            final_votes=votes
        )
    
    async def _quorum_based(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Quorum-based consensus (minimum participation + majority).
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        votes, participating = await self._collect_votes(proposal, agents)
        agreement = self._calculate_agreement_level(votes, len(agents))
        winner = self._get_winning_option(votes)
        
        # Must meet quorum and have majority agreement
        quorum_met = len(participating) >= len(agents) * self.quorum
        consensus_reached = quorum_met and agreement > 0.5
        
        round_data = ConsensusRound(
            round_number=1,
            votes=votes,
            agreement_level=agreement
        )
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=consensus_reached,
            chosen_option=winner if consensus_reached else None,
            agreement_level=agreement,
            rounds=[round_data],
            participating_agents=participating,
            algorithm_used=ConsensusAlgorithm.QUORUM_BASED,
            duration_seconds=0.0,
            final_votes=votes,
            metadata={"quorum_met": quorum_met, "required_quorum": self.quorum}
        )
    
    async def _iterative_refinement(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Iterative refinement - multiple rounds to build consensus.
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        rounds: List[ConsensusRound] = []
        participating_agents: Set[str] = set()
        
        for round_num in range(1, self.max_rounds + 1):
            # Collect votes for this round
            votes, participating = await self._collect_votes(proposal, agents, round_num)
            participating_agents.update(participating)
            
            agreement = self._calculate_agreement_level(votes, len(agents))
            winner = self._get_winning_option(votes)
            
            round_data = ConsensusRound(
                round_number=round_num,
                votes=votes,
                agreement_level=agreement
            )
            rounds.append(round_data)
            
            # Check if consensus reached
            if agreement >= self.agreement_threshold:
                logger.info(f"Consensus reached in round {round_num}")
                return ConsensusResult(
                    proposal_id=proposal.proposal_id,
                    consensus_reached=True,
                    chosen_option=winner,
                    agreement_level=agreement,
                    rounds=rounds,
                    participating_agents=participating_agents,
                    algorithm_used=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
                    duration_seconds=0.0,
                    final_votes=votes
                )
            
            # If not last round, brief pause before next round
            if round_num < self.max_rounds:
                logger.info(
                    f"Round {round_num} agreement {agreement:.2%} below threshold, "
                    f"proceeding to round {round_num + 1}"
                )
                await asyncio.sleep(1)  # Brief pause between rounds
        
        # Consensus not reached after max rounds
        final_votes = rounds[-1].votes if rounds else {}
        final_agreement = rounds[-1].agreement_level if rounds else 0.0
        final_winner = self._get_winning_option(final_votes)
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=False,
            chosen_option=final_winner,  # Best effort winner
            agreement_level=final_agreement,
            rounds=rounds,
            participating_agents=participating_agents,
            algorithm_used=ConsensusAlgorithm.ITERATIVE_REFINEMENT,
            duration_seconds=0.0,
            final_votes=final_votes,
            metadata={"max_rounds_reached": True}
        )
    
    async def _delegated(
        self,
        proposal: ConsensusProposal,
        agents: List[Any]
    ) -> ConsensusResult:
        """Delegated consensus - high-confidence agents decide.
        
        Args:
            proposal: The proposal
            agents: List of agents
            
        Returns:
            ConsensusResult
        """
        votes, participating = await self._collect_votes(proposal, agents)
        
        # Filter to high-confidence agents only
        high_confidence_votes = {
            agent_name: vote
            for agent_name, vote in votes.items()
            if vote.get("confidence", 0) >= 0.7
        }
        
        if not high_confidence_votes:
            # Fall back to all votes if no high-confidence agents
            high_confidence_votes = votes
        
        agreement = self._calculate_agreement_level(high_confidence_votes, len(agents))
        winner = self._get_winning_option(high_confidence_votes)
        
        consensus_reached = agreement >= 0.5 and len(high_confidence_votes) > 0
        
        round_data = ConsensusRound(
            round_number=1,
            votes=votes,
            agreement_level=agreement
        )
        
        return ConsensusResult(
            proposal_id=proposal.proposal_id,
            consensus_reached=consensus_reached,
            chosen_option=winner if consensus_reached else None,
            agreement_level=agreement,
            rounds=[round_data],
            participating_agents=participating,
            algorithm_used=ConsensusAlgorithm.DELEGATED,
            duration_seconds=0.0,
            final_votes=high_confidence_votes,
            metadata={
                "high_confidence_voters": len(high_confidence_votes),
                "total_voters": len(votes)
            }
        )
    
    def get_consensus_statistics(self) -> Dict[str, Any]:
        """Get statistics about consensus building history.
        
        Returns:
            Dictionary with consensus statistics
        """
        if not self.consensus_history:
            return {
                "total_proposals": 0,
                "consensus_rate": 0.0,
                "average_agreement": 0.0,
                "average_rounds": 0.0
            }
        
        total = len(self.consensus_history)
        consensus_reached = sum(1 for r in self.consensus_history if r.consensus_reached)
        avg_agreement = sum(r.agreement_level for r in self.consensus_history) / total
        avg_rounds = sum(len(r.rounds) for r in self.consensus_history) / total
        
        return {
            "total_proposals": total,
            "consensus_rate": consensus_reached / total,
            "average_agreement": avg_agreement,
            "average_rounds": avg_rounds,
            "recent_results": [
                {
                    "proposal": r.proposal_id,
                    "consensus": r.consensus_reached,
                    "agreement": r.agreement_level
                }
                for r in self.consensus_history[-10:]
            ]
        }
