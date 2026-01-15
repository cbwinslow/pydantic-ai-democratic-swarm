"""Pydantic AI Democratic Swarm - Revolutionary AI Agent Orchestration."""

__version__ = "1.0.0"
__author__ = "Pydantic AI Swarm Team"
__description__ = "Democratic AI agent orchestration with efficiency enforcement"

from .core.orchestrator import PydanticAISwarmOrchestrator, TaskResult, SwarmHealth
from .core.base_agent import BaseAgent, ConfidenceMetrics
from .quality.efficiency_enforcer import EfficiencyEnforcer
from .governance.voting import VotingSystem, VotingMethod, Vote, VotingResult
from .governance.consensus import ConsensusBuilder, ConsensusAlgorithm, ConsensusProposal
from .governance.confidence import ConfidenceScore, ConfidenceReport

__all__ = [
    # Core
    "PydanticAISwarmOrchestrator",
    "TaskResult",
    "SwarmHealth",
    "BaseAgent",
    "ConfidenceMetrics",
    # Quality
    "EfficiencyEnforcer",
    # Governance - Voting
    "VotingSystem",
    "VotingMethod",
    "Vote",
    "VotingResult",
    # Governance - Consensus
    "ConsensusBuilder",
    "ConsensusAlgorithm",
    "ConsensusProposal",
    # Governance - Confidence
    "ConfidenceScore",
    "ConfidenceReport",
    # Metadata
    "__version__",
]
