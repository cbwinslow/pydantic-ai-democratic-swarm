"""Monitoring System for Agent Swarm.

Provides health monitoring and performance tracking for the swarm.
"""

import logging
import time
from typing import Any, Dict, List
from dataclasses import dataclass, field
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """A performance metric measurement."""
    metric_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)


class SwarmMonitoring:
    """Monitors swarm health and performance."""
    
    def __init__(self):
        """Initialize swarm monitoring."""
        self.metrics: List[PerformanceMetric] = []
        self.is_monitoring = False
        self.start_time: Optional[float] = None
        self.logger = logging.getLogger("SwarmMonitoring")
    
    async def start_monitoring(self) -> None:
        """Start monitoring the swarm."""
        self.is_monitoring = True
        self.start_time = time.time()
        self.logger.info("Swarm monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring the swarm."""
        self.is_monitoring = False
        self.logger.info("Swarm monitoring stopped")
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            tags: Optional tags for the metric
        """
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            tags=tags or {}
        )
        self.metrics.append(metric)
        self.logger.debug(f"Recorded metric: {metric_name}={value}")
    
    def get_metrics(
        self,
        metric_name: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[PerformanceMetric]:
        """Get recorded metrics.
        
        Args:
            metric_name: Filter by metric name
            since: Only return metrics after this time
            
        Returns:
            List of metrics
        """
        metrics = self.metrics
        
        if metric_name:
            metrics = [m for m in metrics if m.metric_name == metric_name]
        
        if since:
            metrics = [m for m in metrics if m.timestamp > since]
        
        return metrics
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics.
        
        Returns:
            Dictionary with stats
        """
        uptime = time.time() - (self.start_time or time.time())
        
        return {
            "is_monitoring": self.is_monitoring,
            "uptime_seconds": uptime,
            "total_metrics": len(self.metrics),
            "unique_metrics": len(set(m.metric_name for m in self.metrics)),
            "start_time": self.start_time
        }
