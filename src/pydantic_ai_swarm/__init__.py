"""Pydantic AI Democratic Swarm - Revolutionary AI Agent Orchestration."""

__version__ = "1.0.0"
__author__ = "Pydantic AI Swarm Team"
__description__ = "Democratic AI agent orchestration with efficiency enforcement"

from .core.orchestrator import PydanticAISwarmOrchestrator
from .core.base_agent import BaseAgent
from .quality.efficiency_enforcer import EfficiencyEnforcer

__all__ = [
    "PydanticAISwarmOrchestrator",
    "BaseAgent",
    "EfficiencyEnforcer",
    "__version__",
]
