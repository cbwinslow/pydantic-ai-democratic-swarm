"""Governance Module - Democratic Decision Making for Agent Swarm.

This module provides comprehensive voting, consensus-building, and confidence
tracking mechanisms for democratic agent coordination.
"""

from .voting import (
    VotingMethod,
    Vote,
    RankedVote,
    ApprovalVote,
    VotingResult,
    VotingSystem,
)
from .consensus import (
    ConsensusAlgorithm,
    ConsensusProposal,
    ConsensusRound,
    ConsensusResult,
    ConsensusBuilder,
)
from .confidence import (
    ConfidenceScore,
    ConfidenceReport,
    calculate_weighted_confidence,
    calculate_task_confidence,
    calculate_voting_weight,
    update_confidence_with_decay,
    update_confidence_with_feedback,
    calculate_confidence_interval,
    assess_confidence_calibration,
    analyze_confidence_trend,
    generate_confidence_recommendations,
    create_confidence_report,
)

__all__ = [
    # Voting
    "VotingMethod",
    "Vote",
    "RankedVote",
    "ApprovalVote",
    "VotingResult",
    "VotingSystem",
    # Consensus
    "ConsensusAlgorithm",
    "ConsensusProposal",
    "ConsensusRound",
    "ConsensusResult",
    "ConsensusBuilder",
    # Confidence
    "ConfidenceScore",
    "ConfidenceReport",
    "calculate_weighted_confidence",
    "calculate_task_confidence",
    "calculate_voting_weight",
    "update_confidence_with_decay",
    "update_confidence_with_feedback",
    "calculate_confidence_interval",
    "assess_confidence_calibration",
    "analyze_confidence_trend",
    "generate_confidence_recommendations",
    "create_confidence_report",
]
