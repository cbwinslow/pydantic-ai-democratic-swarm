"""Observability and monitoring for Pydantic AI Swarm.

This module provides comprehensive monitoring, metrics collection,
and observability features including Prometheus and OpenTelemetry integration.
"""

import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import structlog
from enum import Enum

# Optional dependencies - will gracefully degrade if not available
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False

logger = structlog.get_logger(__name__)


class MetricType(str, Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    description: str
    metric_type: MetricType
    labels: List[str] = field(default_factory=list)


class ObservabilityManager:
    """Manages observability features for the swarm.
    
    Provides:
    - Prometheus metrics export
    - OpenTelemetry tracing
    - Structured logging
    - Health checks
    - Performance monitoring
    
    Example:
        >>> obs = ObservabilityManager(
        ...     prometheus_enabled=True,
        ...     prometheus_port=9090
        ... )
        >>> obs.start()
        >>> obs.record_task_execution(duration=1.5, success=True)
    """
    
    def __init__(
        self,
        service_name: str = "pydantic-ai-swarm",
        prometheus_enabled: bool = False,
        prometheus_port: int = 9090,
        otel_enabled: bool = False,
        otel_endpoint: Optional[str] = None,
    ) -> None:
        """Initialize observability manager.
        
        Args:
            service_name: Name of the service for identification
            prometheus_enabled: Enable Prometheus metrics
            prometheus_port: Port for Prometheus metrics endpoint
            otel_enabled: Enable OpenTelemetry tracing
            otel_endpoint: OpenTelemetry collector endpoint
        """
        self.service_name = service_name
        self.prometheus_enabled = prometheus_enabled and PROMETHEUS_AVAILABLE
        self.prometheus_port = prometheus_port
        self.otel_enabled = otel_enabled and OTEL_AVAILABLE
        self.otel_endpoint = otel_endpoint
        
        self._metrics: Dict[str, Any] = {}
        self._tracer: Optional[Any] = None
        self._started = False
        
        if self.prometheus_enabled:
            self._initialize_prometheus_metrics()
        
        if self.otel_enabled:
            self._initialize_opentelemetry()
    
    def _initialize_prometheus_metrics(self) -> None:
        """Initialize Prometheus metrics."""
        if not PROMETHEUS_AVAILABLE:
            logger.warning("prometheus_unavailable", 
                          message="prometheus_client not installed")
            return
        
        # Task metrics
        self._metrics["tasks_total"] = Counter(
            "swarm_tasks_total",
            "Total number of tasks executed",
            ["status", "agent_type"]
        )
        
        self._metrics["task_duration"] = Histogram(
            "swarm_task_duration_seconds",
            "Task execution duration in seconds",
            ["agent_type", "domain"]
        )
        
        self._metrics["task_confidence"] = Histogram(
            "swarm_task_confidence_score",
            "Task confidence scores",
            ["agent_type"]
        )
        
        # Voting metrics
        self._metrics["votes_total"] = Counter(
            "swarm_votes_total",
            "Total number of votes cast",
            ["voting_method"]
        )
        
        self._metrics["consensus_attempts"] = Counter(
            "swarm_consensus_attempts_total",
            "Total consensus building attempts",
            ["algorithm", "result"]
        )
        
        # Agent metrics
        self._metrics["agents_active"] = Gauge(
            "swarm_agents_active",
            "Number of active agents"
        )
        
        self._metrics["agent_tasks"] = Counter(
            "swarm_agent_tasks_total",
            "Tasks executed by agent",
            ["agent_name", "status"]
        )
        
        # System metrics
        self._metrics["errors_total"] = Counter(
            "swarm_errors_total",
            "Total number of errors",
            ["error_type", "component"]
        )
        
        self._metrics["efficiency_score"] = Gauge(
            "swarm_efficiency_score",
            "Current efficiency score"
        )
        
        logger.info("prometheus_initialized",
                   metrics_count=len(self._metrics))
    
    def _initialize_opentelemetry(self) -> None:
        """Initialize OpenTelemetry tracing."""
        if not OTEL_AVAILABLE:
            logger.warning("opentelemetry_unavailable",
                          message="opentelemetry not installed")
            return
        
        try:
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "1.0.0",
            })
            
            provider = TracerProvider(resource=resource)
            
            if self.otel_endpoint:
                exporter = OTLPSpanExporter(endpoint=self.otel_endpoint)
                processor = BatchSpanProcessor(exporter)
                provider.add_span_processor(processor)
            
            trace.set_tracer_provider(provider)
            self._tracer = trace.get_tracer(__name__)
            
            logger.info("opentelemetry_initialized",
                       endpoint=self.otel_endpoint)
            
        except Exception as e:
            logger.error("opentelemetry_init_failed", error=str(e))
    
    def start(self) -> None:
        """Start observability services."""
        if self._started:
            logger.warning("observability_already_started")
            return
        
        if self.prometheus_enabled:
            try:
                start_http_server(self.prometheus_port)
                logger.info("prometheus_server_started",
                           port=self.prometheus_port)
            except Exception as e:
                logger.error("prometheus_start_failed",
                           port=self.prometheus_port,
                           error=str(e))
        
        self._started = True
        logger.info("observability_started",
                   prometheus=self.prometheus_enabled,
                   opentelemetry=self.otel_enabled)
    
    def record_task_execution(
        self,
        duration: float,
        success: bool,
        agent_type: str = "unknown",
        domain: str = "general",
        confidence: Optional[float] = None,
    ) -> None:
        """Record task execution metrics.
        
        Args:
            duration: Task duration in seconds
            success: Whether task succeeded
            agent_type: Type of agent that executed the task
            domain: Task domain
            confidence: Confidence score if available
        """
        status = "success" if success else "failure"
        
        if self.prometheus_enabled and "tasks_total" in self._metrics:
            self._metrics["tasks_total"].labels(
                status=status,
                agent_type=agent_type
            ).inc()
            
            self._metrics["task_duration"].labels(
                agent_type=agent_type,
                domain=domain
            ).observe(duration)
            
            if confidence is not None:
                self._metrics["task_confidence"].labels(
                    agent_type=agent_type
                ).observe(confidence)
        
        logger.info("task_executed",
                   duration=duration,
                   success=success,
                   agent_type=agent_type,
                   domain=domain,
                   confidence=confidence)
    
    def record_vote(
        self,
        voting_method: str,
        participants: int,
        duration: float,
    ) -> None:
        """Record voting metrics.
        
        Args:
            voting_method: Method used for voting
            participants: Number of participants
            duration: Vote duration in seconds
        """
        if self.prometheus_enabled and "votes_total" in self._metrics:
            self._metrics["votes_total"].labels(
                voting_method=voting_method
            ).inc()
        
        logger.info("vote_recorded",
                   voting_method=voting_method,
                   participants=participants,
                   duration=duration)
    
    def record_consensus(
        self,
        algorithm: str,
        reached: bool,
        attempts: int,
        duration: float,
    ) -> None:
        """Record consensus building metrics.
        
        Args:
            algorithm: Consensus algorithm used
            reached: Whether consensus was reached
            attempts: Number of attempts
            duration: Total duration in seconds
        """
        result = "success" if reached else "failure"
        
        if self.prometheus_enabled and "consensus_attempts" in self._metrics:
            self._metrics["consensus_attempts"].labels(
                algorithm=algorithm,
                result=result
            ).inc()
        
        logger.info("consensus_recorded",
                   algorithm=algorithm,
                   reached=reached,
                   attempts=attempts,
                   duration=duration)
    
    def record_agent_activity(
        self,
        agent_name: str,
        task_executed: bool = False,
        error: bool = False,
    ) -> None:
        """Record agent activity metrics.
        
        Args:
            agent_name: Name of the agent
            task_executed: Whether a task was executed
            error: Whether an error occurred
        """
        if task_executed and self.prometheus_enabled:
            if "agent_tasks" in self._metrics:
                status = "error" if error else "success"
                self._metrics["agent_tasks"].labels(
                    agent_name=agent_name,
                    status=status
                ).inc()
        
        logger.debug("agent_activity",
                    agent_name=agent_name,
                    task_executed=task_executed,
                    error=error)
    
    def update_active_agents(self, count: int) -> None:
        """Update active agents count.
        
        Args:
            count: Number of currently active agents
        """
        if self.prometheus_enabled and "agents_active" in self._metrics:
            self._metrics["agents_active"].set(count)
        
        logger.debug("agents_active_updated", count=count)
    
    def record_error(
        self,
        error_type: str,
        component: str,
        details: Optional[str] = None,
    ) -> None:
        """Record error occurrence.
        
        Args:
            error_type: Type/category of error
            component: Component where error occurred
            details: Optional error details
        """
        if self.prometheus_enabled and "errors_total" in self._metrics:
            self._metrics["errors_total"].labels(
                error_type=error_type,
                component=component
            ).inc()
        
        logger.error("error_recorded",
                    error_type=error_type,
                    component=component,
                    details=details)
    
    def update_efficiency_score(self, score: float) -> None:
        """Update efficiency score.
        
        Args:
            score: Efficiency score (0.0 to 1.0)
        """
        if self.prometheus_enabled and "efficiency_score" in self._metrics:
            self._metrics["efficiency_score"].set(score)
        
        logger.info("efficiency_score_updated", score=score)
    
    def create_span(self, name: str) -> Any:
        """Create a tracing span.
        
        Args:
            name: Span name
            
        Returns:
            Span context manager or no-op context
        """
        if self._tracer:
            return self._tracer.start_as_current_span(name)
        else:
            # Return a no-op context manager
            from contextlib import nullcontext
            return nullcontext()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of observability systems.
        
        Returns:
            Health status dictionary
        """
        return {
            "healthy": True,
            "service_name": self.service_name,
            "prometheus": {
                "enabled": self.prometheus_enabled,
                "available": PROMETHEUS_AVAILABLE,
                "port": self.prometheus_port if self.prometheus_enabled else None,
            },
            "opentelemetry": {
                "enabled": self.otel_enabled,
                "available": OTEL_AVAILABLE,
                "endpoint": self.otel_endpoint if self.otel_enabled else None,
            },
            "metrics_count": len(self._metrics),
            "started": self._started,
        }


# Global observability manager instance
_global_observability: Optional[ObservabilityManager] = None


def get_observability_manager() -> ObservabilityManager:
    """Get or create global observability manager.
    
    Returns:
        Global ObservabilityManager instance
    """
    global _global_observability
    if _global_observability is None:
        _global_observability = ObservabilityManager()
    return _global_observability


def initialize_observability(
    prometheus_enabled: bool = False,
    prometheus_port: int = 9090,
    otel_enabled: bool = False,
    otel_endpoint: Optional[str] = None,
) -> ObservabilityManager:
    """Initialize global observability manager.
    
    Args:
        prometheus_enabled: Enable Prometheus metrics
        prometheus_port: Port for Prometheus metrics endpoint
        otel_enabled: Enable OpenTelemetry tracing
        otel_endpoint: OpenTelemetry collector endpoint
        
    Returns:
        Initialized ObservabilityManager
    """
    global _global_observability
    _global_observability = ObservabilityManager(
        prometheus_enabled=prometheus_enabled,
        prometheus_port=prometheus_port,
        otel_enabled=otel_enabled,
        otel_endpoint=otel_endpoint,
    )
    _global_observability.start()
    return _global_observability
