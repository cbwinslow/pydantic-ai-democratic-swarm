"""Configuration management for Pydantic AI Swarm.

This module provides configuration classes for swarm orchestration,
agent settings, and system-wide parameters.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import os


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class VotingMethodConfig(str, Enum):
    """Available voting methods."""
    PLURALITY = "plurality"
    WEIGHTED = "weighted"
    RANKED_CHOICE = "ranked_choice"
    APPROVAL = "approval"
    CONSENSUS = "consensus"


class ConsensusAlgorithmConfig(str, Enum):
    """Available consensus algorithms."""
    SIMPLE_MAJORITY = "simple_majority"
    SUPERMAJORITY = "supermajority"
    UNANIMOUS = "unanimous"
    QUORUM_BASED = "quorum_based"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    DELEGATED = "delegated"


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and observability."""
    
    enabled: bool = Field(default=True, description="Enable monitoring")
    prometheus_enabled: bool = Field(default=False, description="Enable Prometheus metrics")
    prometheus_port: int = Field(default=9090, ge=1024, le=65535)
    opentelemetry_enabled: bool = Field(default=False, description="Enable OpenTelemetry")
    otel_endpoint: Optional[str] = Field(default=None, description="OpenTelemetry endpoint")
    metrics_interval: int = Field(default=60, ge=10, description="Metrics collection interval (seconds)")
    health_check_interval: int = Field(default=30, ge=5, description="Health check interval (seconds)")


class RedisConfig(BaseModel):
    """Redis configuration for distributed state."""
    
    enabled: bool = Field(default=False, description="Enable Redis backend")
    host: str = Field(default="localhost")
    port: int = Field(default=6379, ge=1, le=65535)
    db: int = Field(default=0, ge=0)
    password: Optional[str] = Field(default=None)
    ssl: bool = Field(default=False)
    connection_pool_size: int = Field(default=10, ge=1)
    
    @classmethod
    def from_env(cls) -> "RedisConfig":
        """Create Redis config from environment variables."""
        return cls(
            enabled=os.getenv("REDIS_ENABLED", "false").lower() == "true",
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
        )


class MQTTConfig(BaseModel):
    """MQTT configuration for agent communication."""
    
    enabled: bool = Field(default=False, description="Enable MQTT communication")
    broker_host: str = Field(default="localhost")
    broker_port: int = Field(default=1883, ge=1, le=65535)
    username: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    topic_prefix: str = Field(default="swarm")
    qos: int = Field(default=1, ge=0, le=2)
    
    @classmethod
    def from_env(cls) -> "MQTTConfig":
        """Create MQTT config from environment variables."""
        return cls(
            enabled=os.getenv("MQTT_ENABLED", "false").lower() == "true",
            broker_host=os.getenv("MQTT_HOST", "localhost"),
            broker_port=int(os.getenv("MQTT_PORT", "1883")),
            username=os.getenv("MQTT_USERNAME"),
            password=os.getenv("MQTT_PASSWORD"),
            topic_prefix=os.getenv("MQTT_TOPIC_PREFIX", "swarm"),
        )


class OpenAIConfig(BaseModel):
    """OpenAI API configuration."""
    
    api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    model: str = Field(default="gpt-4", description="Default model to use")
    max_tokens: int = Field(default=2000, ge=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    timeout: int = Field(default=30, ge=1, description="API timeout (seconds)")
    
    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Create OpenAI config from environment variables."""
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        )


class SwarmConfig(BaseModel):
    """Main swarm configuration."""
    
    name: str = Field(default="PydanticAISwarm", description="Swarm name")
    description: Optional[str] = Field(default=None, description="Swarm description")
    
    # Voting and consensus
    voting_method: VotingMethodConfig = Field(default=VotingMethodConfig.WEIGHTED)
    consensus_algorithm: ConsensusAlgorithmConfig = Field(default=ConsensusAlgorithmConfig.SUPERMAJORITY)
    consensus_threshold: float = Field(default=0.66, ge=0.0, le=1.0)
    min_confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Task execution
    max_concurrent_tasks: int = Field(default=10, ge=1)
    task_timeout: int = Field(default=300, ge=1, description="Task timeout (seconds)")
    enable_task_retry: bool = Field(default=True)
    max_retry_attempts: int = Field(default=3, ge=1)
    
    # Efficiency enforcement
    enable_efficiency_enforcer: bool = Field(default=True)
    duplicate_detection_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    code_reuse_enforcement: bool = Field(default=True)
    
    # Monitoring
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    # External services
    redis: RedisConfig = Field(default_factory=RedisConfig)
    mqtt: MQTTConfig = Field(default_factory=MQTTConfig)
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    
    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_to_file: bool = Field(default=False)
    log_file_path: Optional[Path] = Field(default=None)
    
    @field_validator("log_file_path", mode="before")
    @classmethod
    def validate_log_path(cls, v: Any) -> Optional[Path]:
        """Validate and convert log file path."""
        if v is None:
            return None
        path = Path(v)
        # Create parent directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        return path
    
    @classmethod
    def from_yaml(cls, path: Path) -> "SwarmConfig":
        """Load configuration from YAML file."""
        import yaml
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    @classmethod
    def from_env(cls, name: str = "PydanticAISwarm") -> "SwarmConfig":
        """Create configuration from environment variables."""
        return cls(
            name=os.getenv("SWARM_NAME", name),
            voting_method=VotingMethodConfig(os.getenv("SWARM_VOTING_METHOD", "weighted")),
            consensus_threshold=float(os.getenv("SWARM_CONSENSUS_THRESHOLD", "0.66")),
            max_concurrent_tasks=int(os.getenv("SWARM_MAX_TASKS", "10")),
            log_level=LogLevel(os.getenv("LOG_LEVEL", "INFO")),
            monitoring=MonitoringConfig(
                enabled=os.getenv("MONITORING_ENABLED", "true").lower() == "true",
                prometheus_enabled=os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true",
                opentelemetry_enabled=os.getenv("OTEL_ENABLED", "false").lower() == "true",
            ),
            redis=RedisConfig.from_env(),
            mqtt=MQTTConfig.from_env(),
            openai=OpenAIConfig.from_env(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump(mode="json", exclude_none=True)


class AgentConfig(BaseModel):
    """Configuration for individual agents."""
    
    name: str = Field(..., description="Agent name")
    agent_type: str = Field(..., description="Agent type/class")
    domain_expertise: List[str] = Field(default_factory=list, description="Domain expertise areas")
    
    # Confidence settings
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    confidence_weight: float = Field(default=1.0, ge=0.0, description="Weight for voting")
    
    # Task execution
    max_concurrent_tasks: int = Field(default=3, ge=1)
    task_timeout: int = Field(default=180, ge=1)
    
    # Tools
    available_tools: List[str] = Field(default_factory=list)
    
    # AI Model configuration (if using AI model)
    ai_model_settings: Optional[Dict[str, Any]] = Field(default=None, description="AI model settings")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump(mode="json", exclude_none=True)


# Default configurations
DEFAULT_SWARM_CONFIG = SwarmConfig()
