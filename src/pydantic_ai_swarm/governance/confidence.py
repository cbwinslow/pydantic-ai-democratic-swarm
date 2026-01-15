"""Confidence Metrics and Utilities for Democratic Decision Making.

This module provides utilities for calculating, tracking, and analyzing
confidence metrics that influence democratic decision-making in the swarm.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import math
import logging


logger = logging.getLogger(__name__)


@dataclass
class ConfidenceScore:
    """Represents a confidence score with context."""
    value: float  # 0.0 to 1.0
    agent_name: str
    domain: str
    timestamp: datetime = field(default_factory=datetime.now)
    factors: Dict[str, float] = field(default_factory=dict)
    reasoning: str = ""
    
    def __post_init__(self):
        """Validate confidence score."""
        if not 0 <= self.value <= 1:
            raise ValueError(f"Confidence value must be between 0 and 1, got {self.value}")


@dataclass
class ConfidenceReport:
    """Comprehensive confidence analysis report."""
    agent_name: str
    overall_confidence: float
    domain_confidences: Dict[str, float]
    recent_performance: float
    voting_accuracy: float
    communication_effectiveness: float
    trend: str  # "improving", "stable", "declining"
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


def calculate_weighted_confidence(
    base_confidence: float,
    weights: Dict[str, float],
    factors: Dict[str, float]
) -> float:
    """Calculate weighted confidence from multiple factors.
    
    Args:
        base_confidence: Base confidence value
        weights: Weight for each factor
        factors: Factor values
        
    Returns:
        Weighted confidence score (0-1)
    """
    if not factors or not weights:
        return base_confidence
    
    weighted_sum = base_confidence * weights.get("base", 0.5)
    weight_total = weights.get("base", 0.5)
    
    for factor_name, factor_value in factors.items():
        weight = weights.get(factor_name, 0.1)
        weighted_sum += factor_value * weight
        weight_total += weight
    
    if weight_total == 0:
        return base_confidence
    
    return max(0.0, min(1.0, weighted_sum / weight_total))


def calculate_task_confidence(
    agent_domains: Dict[str, float],
    agent_tools: Dict[str, float],
    task_domain: str,
    required_tools: List[str],
    recent_performance: List[bool],
    base_confidence: float = 0.5
) -> float:
    """Calculate agent confidence for a specific task.
    
    Args:
        agent_domains: Domain expertise scores
        agent_tools: Tool confidence scores
        task_domain: Task domain
        required_tools: Tools required for task
        recent_performance: Recent task success history
        base_confidence: Base confidence level
        
    Returns:
        Task confidence score (0-1)
    """
    # Domain match confidence
    domain_confidence = agent_domains.get(task_domain, 0.3)
    
    # Tool confidence
    if required_tools:
        tool_confidences = [agent_tools.get(tool, 0.3) for tool in required_tools]
        tool_confidence = sum(tool_confidences) / len(tool_confidences)
    else:
        tool_confidence = 0.5
    
    # Recent performance
    if recent_performance:
        performance_rate = sum(recent_performance) / len(recent_performance)
    else:
        performance_rate = 0.5
    
    # Weighted combination
    weights = {
        "domain": 0.4,
        "tools": 0.3,
        "performance": 0.3
    }
    
    confidence = (
        domain_confidence * weights["domain"] +
        tool_confidence * weights["tools"] +
        performance_rate * weights["performance"]
    )
    
    return max(0.0, min(1.0, confidence))


def calculate_voting_weight(
    confidence: float,
    domain_expertise: float,
    participation_history: int,
    voting_accuracy: float,
    min_weight: float = 0.1,
    max_weight: float = 2.0
) -> float:
    """Calculate voting weight for an agent.
    
    Args:
        confidence: Overall confidence
        domain_expertise: Expertise in relevant domain
        participation_history: Number of past participations
        voting_accuracy: Historical voting accuracy
        min_weight: Minimum weight
        max_weight: Maximum weight
        
    Returns:
        Voting weight (clamped between min and max)
    """
    # Base weight from confidence
    base_weight = confidence
    
    # Boost for domain expertise
    expertise_boost = domain_expertise * 0.3
    
    # Boost for participation (with diminishing returns)
    participation_boost = min(0.2, participation_history / 100)
    
    # Boost for accuracy
    accuracy_boost = (voting_accuracy - 0.5) * 0.3  # Can be negative
    
    # Combine factors
    weight = base_weight + expertise_boost + participation_boost + accuracy_boost
    
    # Clamp to range
    return max(min_weight, min(max_weight, weight))


def update_confidence_with_decay(
    current_confidence: float,
    time_since_update: timedelta,
    decay_rate: float = 0.01
) -> float:
    """Apply time decay to confidence score.
    
    Confidence slowly decays over time to encourage continued validation.
    
    Args:
        current_confidence: Current confidence value
        time_since_update: Time since last update
        decay_rate: Decay rate per day
        
    Returns:
        Decayed confidence value
    """
    days_elapsed = time_since_update.total_seconds() / 86400
    decay_factor = math.exp(-decay_rate * days_elapsed)
    
    # Decay towards neutral 0.5
    neutral = 0.5
    decayed = neutral + (current_confidence - neutral) * decay_factor
    
    return max(0.0, min(1.0, decayed))


def update_confidence_with_feedback(
    current_confidence: float,
    outcome_success: bool,
    learning_rate: float = 0.1
) -> float:
    """Update confidence based on outcome feedback.
    
    Uses exponential moving average to update confidence.
    
    Args:
        current_confidence: Current confidence value
        outcome_success: Whether outcome was successful
        learning_rate: How quickly to learn from feedback
        
    Returns:
        Updated confidence value
    """
    target = 1.0 if outcome_success else 0.0
    updated = current_confidence + learning_rate * (target - current_confidence)
    
    return max(0.0, min(1.0, updated))


def calculate_confidence_interval(
    confidence: float,
    sample_size: int,
    confidence_level: float = 0.95
) -> Tuple[float, float]:
    """Calculate confidence interval for a confidence score.
    
    Args:
        confidence: Point estimate of confidence
        sample_size: Number of samples
        confidence_level: Desired confidence level (e.g., 0.95 for 95%)
        
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if sample_size < 1:
        return (0.0, 1.0)
    
    # Use Wilson score interval for proportions
    z = 1.96 if confidence_level >= 0.95 else 1.645  # z-score
    
    denominator = 1 + (z ** 2) / sample_size
    center = confidence + (z ** 2) / (2 * sample_size)
    margin = z * math.sqrt(
        (confidence * (1 - confidence) + (z ** 2) / (4 * sample_size)) / sample_size
    )
    
    lower = (center - margin) / denominator
    upper = (center + margin) / denominator
    
    return (max(0.0, lower), min(1.0, upper))


def assess_confidence_calibration(
    predicted_confidences: List[float],
    actual_outcomes: List[bool]
) -> Dict[str, float]:
    """Assess how well-calibrated confidence predictions are.
    
    Args:
        predicted_confidences: List of predicted confidence values
        actual_outcomes: List of actual success/failure outcomes
        
    Returns:
        Dictionary with calibration metrics
    """
    if len(predicted_confidences) != len(actual_outcomes):
        raise ValueError("Lists must have same length")
    
    if not predicted_confidences:
        return {
            "calibration_error": 0.0,
            "brier_score": 0.0,
            "accuracy": 0.0
        }
    
    n = len(predicted_confidences)
    
    # Calibration error (mean absolute difference)
    calibration_error = sum(
        abs(conf - (1.0 if outcome else 0.0))
        for conf, outcome in zip(predicted_confidences, actual_outcomes)
    ) / n
    
    # Brier score (mean squared error)
    brier_score = sum(
        (conf - (1.0 if outcome else 0.0)) ** 2
        for conf, outcome in zip(predicted_confidences, actual_outcomes)
    ) / n
    
    # Accuracy (treating confidence > 0.5 as positive prediction)
    correct = sum(
        1 for conf, outcome in zip(predicted_confidences, actual_outcomes)
        if (conf > 0.5) == outcome
    )
    accuracy = correct / n
    
    return {
        "calibration_error": calibration_error,
        "brier_score": brier_score,
        "accuracy": accuracy,
        "sample_size": n
    }


def analyze_confidence_trend(
    historical_confidences: List[Tuple[datetime, float]],
    window_days: int = 30
) -> str:
    """Analyze trend in confidence over time.
    
    Args:
        historical_confidences: List of (timestamp, confidence) tuples
        window_days: Number of days to analyze
        
    Returns:
        Trend description: "improving", "stable", or "declining"
    """
    if len(historical_confidences) < 2:
        return "stable"
    
    # Filter to recent window
    cutoff = datetime.now() - timedelta(days=window_days)
    recent = [(t, c) for t, c in historical_confidences if t >= cutoff]
    
    if len(recent) < 2:
        return "stable"
    
    # Calculate linear trend
    n = len(recent)
    times = [(t - recent[0][0]).total_seconds() for t, _ in recent]
    confidences = [c for _, c in recent]
    
    # Simple linear regression
    mean_time = sum(times) / n
    mean_conf = sum(confidences) / n
    
    numerator = sum((t - mean_time) * (c - mean_conf) for t, c in zip(times, confidences))
    denominator = sum((t - mean_time) ** 2 for t in times)
    
    if denominator == 0:
        return "stable"
    
    slope = numerator / denominator
    
    # Classify trend
    if slope > 0.00001:  # Improving
        return "improving"
    elif slope < -0.00001:  # Declining
        return "declining"
    else:
        return "stable"


def generate_confidence_recommendations(
    agent_name: str,
    overall_confidence: float,
    domain_confidences: Dict[str, float],
    recent_performance: float,
    voting_accuracy: float,
    trend: str
) -> List[str]:
    """Generate recommendations for improving confidence.
    
    Args:
        agent_name: Name of the agent
        overall_confidence: Overall confidence score
        domain_confidences: Domain-specific confidences
        recent_performance: Recent performance rate
        voting_accuracy: Voting accuracy rate
        trend: Confidence trend
        
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Overall confidence
    if overall_confidence < 0.5:
        recommendations.append(
            "Overall confidence is low. Consider focusing on core competencies."
        )
    elif overall_confidence > 0.8:
        recommendations.append(
            "High overall confidence. Consider mentoring other agents."
        )
    
    # Domain expertise
    weak_domains = [d for d, c in domain_confidences.items() if c < 0.5]
    if weak_domains:
        recommendations.append(
            f"Consider training in domains: {', '.join(weak_domains[:3])}"
        )
    
    strong_domains = [d for d, c in domain_confidences.items() if c > 0.8]
    if strong_domains:
        recommendations.append(
            f"Leverage expertise in: {', '.join(strong_domains[:3])}"
        )
    
    # Performance
    if recent_performance < 0.6:
        recommendations.append(
            "Recent performance below expectations. Review recent failures."
        )
    elif recent_performance > 0.85:
        recommendations.append(
            "Excellent recent performance. Take on more challenging tasks."
        )
    
    # Voting accuracy
    if voting_accuracy < 0.6:
        recommendations.append(
            "Voting accuracy could improve. Be more selective in task selection."
        )
    elif voting_accuracy > 0.8:
        recommendations.append(
            "Strong voting accuracy. Your judgment is reliable."
        )
    
    # Trend
    if trend == "declining":
        recommendations.append(
            "Confidence declining. Consider taking a break or seeking support."
        )
    elif trend == "improving":
        recommendations.append(
            "Confidence improving. Continue current approach."
        )
    
    return recommendations


def create_confidence_report(
    agent_name: str,
    confidence_metrics: Any,  # ConfidenceMetrics from base_agent
    window_days: int = 30
) -> ConfidenceReport:
    """Create a comprehensive confidence report for an agent.
    
    Args:
        agent_name: Name of the agent
        confidence_metrics: ConfidenceMetrics object from agent
        window_days: Days to analyze for trends
        
    Returns:
        ConfidenceReport with analysis and recommendations
    """
    # Calculate recent performance
    recent_performance = (
        sum(confidence_metrics.recent_performance) / len(confidence_metrics.recent_performance)
        if confidence_metrics.recent_performance
        else 0.5
    )
    
    # Calculate voting accuracy
    voting_accuracy = (
        confidence_metrics.successful_votes / confidence_metrics.total_votes
        if confidence_metrics.total_votes > 0
        else 0.5
    )
    
    # Calculate communication effectiveness
    comm_effectiveness = (
        confidence_metrics.effective_communications / confidence_metrics.total_communications
        if confidence_metrics.total_communications > 0
        else 0.5
    )
    
    # Analyze trend (would need historical data in practice)
    trend = "stable"  # Simplified - would analyze historical data
    
    # Generate recommendations
    recommendations = generate_confidence_recommendations(
        agent_name=agent_name,
        overall_confidence=confidence_metrics.overall,
        domain_confidences=confidence_metrics.domains,
        recent_performance=recent_performance,
        voting_accuracy=voting_accuracy,
        trend=trend
    )
    
    return ConfidenceReport(
        agent_name=agent_name,
        overall_confidence=confidence_metrics.overall,
        domain_confidences=dict(confidence_metrics.domains),
        recent_performance=recent_performance,
        voting_accuracy=voting_accuracy,
        communication_effectiveness=comm_effectiveness,
        trend=trend,
        recommendations=recommendations
    )
