"""Tests for configuration module."""

import pytest
from pathlib import Path
import tempfile
import os

from pydantic_ai_swarm.core.config import (
    SwarmConfig,
    AgentConfig,
    MonitoringConfig,
    RedisConfig,
    MQTTConfig,
    OpenAIConfig,
    VotingMethodConfig,
    ConsensusAlgorithmConfig,
    LogLevel,
)


@pytest.mark.unit
class TestSwarmConfig:
    """Test cases for SwarmConfig."""
    
    def test_default_config_creation(self):
        """Test default config can be created."""
        config = SwarmConfig()
        assert config.name == "PydanticAISwarm"
        assert config.voting_method == VotingMethodConfig.WEIGHTED
        assert config.consensus_algorithm == ConsensusAlgorithmConfig.SUPERMAJORITY
        assert config.consensus_threshold == 0.66
    
    def test_custom_config_creation(self):
        """Test custom config creation."""
        config = SwarmConfig(
            name="CustomSwarm",
            voting_method=VotingMethodConfig.PLURALITY,
            consensus_threshold=0.75,
            max_concurrent_tasks=20,
        )
        assert config.name == "CustomSwarm"
        assert config.voting_method == VotingMethodConfig.PLURALITY
        assert config.consensus_threshold == 0.75
        assert config.max_concurrent_tasks == 20
    
    def test_config_validation_consensus_threshold(self):
        """Test consensus threshold validation."""
        # Valid threshold
        config = SwarmConfig(consensus_threshold=0.5)
        assert config.consensus_threshold == 0.5
        
        # Invalid threshold should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            SwarmConfig(consensus_threshold=1.5)
    
    def test_config_to_dict(self):
        """Test config conversion to dictionary."""
        config = SwarmConfig(name="TestSwarm")
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "TestSwarm"
        assert "voting_method" in config_dict
        assert "monitoring" in config_dict
    
    def test_config_from_env(self, monkeypatch):
        """Test config creation from environment variables."""
        monkeypatch.setenv("SWARM_NAME", "EnvSwarm")
        monkeypatch.setenv("SWARM_VOTING_METHOD", "plurality")
        monkeypatch.setenv("SWARM_CONSENSUS_THRESHOLD", "0.8")
        monkeypatch.setenv("SWARM_MAX_TASKS", "15")
        
        config = SwarmConfig.from_env()
        assert config.name == "EnvSwarm"
        assert config.voting_method == VotingMethodConfig.PLURALITY
        assert config.consensus_threshold == 0.8
        assert config.max_concurrent_tasks == 15
    
    def test_config_yaml_roundtrip(self, tmp_path):
        """Test saving and loading config from YAML."""
        config = SwarmConfig(
            name="YAMLSwarm",
            max_concurrent_tasks=25,
        )
        
        yaml_path = tmp_path / "config.yaml"
        
        # Save to YAML
        import yaml
        with open(yaml_path, "w") as f:
            yaml.dump(config.to_dict(), f)
        
        # Load from YAML
        loaded_config = SwarmConfig.from_yaml(yaml_path)
        assert loaded_config.name == "YAMLSwarm"
        assert loaded_config.max_concurrent_tasks == 25


@pytest.mark.unit
class TestMonitoringConfig:
    """Test cases for MonitoringConfig."""
    
    def test_default_monitoring_config(self):
        """Test default monitoring config."""
        config = MonitoringConfig()
        assert config.enabled is True
        assert config.prometheus_enabled is False
        assert config.prometheus_port == 9090
        assert config.opentelemetry_enabled is False
    
    def test_custom_monitoring_config(self):
        """Test custom monitoring config."""
        config = MonitoringConfig(
            prometheus_enabled=True,
            prometheus_port=8080,
            opentelemetry_enabled=True,
            otel_endpoint="http://localhost:4317",
        )
        assert config.prometheus_enabled is True
        assert config.prometheus_port == 8080
        assert config.opentelemetry_enabled is True
        assert config.otel_endpoint == "http://localhost:4317"
    
    def test_port_validation(self):
        """Test port number validation."""
        # Valid port
        config = MonitoringConfig(prometheus_port=9090)
        assert config.prometheus_port == 9090
        
        # Invalid port should raise validation error
        with pytest.raises(Exception):
            MonitoringConfig(prometheus_port=99999)


@pytest.mark.unit
class TestRedisConfig:
    """Test cases for RedisConfig."""
    
    def test_default_redis_config(self):
        """Test default Redis config."""
        config = RedisConfig()
        assert config.enabled is False
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
    
    def test_redis_from_env(self, monkeypatch):
        """Test Redis config from environment."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("REDIS_PORT", "6380")
        monkeypatch.setenv("REDIS_DB", "1")
        
        config = RedisConfig.from_env()
        assert config.enabled is True
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1


@pytest.mark.unit
class TestMQTTConfig:
    """Test cases for MQTTConfig."""
    
    def test_default_mqtt_config(self):
        """Test default MQTT config."""
        config = MQTTConfig()
        assert config.enabled is False
        assert config.broker_host == "localhost"
        assert config.broker_port == 1883
        assert config.topic_prefix == "swarm"
    
    def test_mqtt_from_env(self, monkeypatch):
        """Test MQTT config from environment."""
        monkeypatch.setenv("MQTT_ENABLED", "true")
        monkeypatch.setenv("MQTT_HOST", "mqtt.example.com")
        monkeypatch.setenv("MQTT_PORT", "1884")
        monkeypatch.setenv("MQTT_TOPIC_PREFIX", "myswarm")
        
        config = MQTTConfig.from_env()
        assert config.enabled is True
        assert config.broker_host == "mqtt.example.com"
        assert config.broker_port == 1884
        assert config.topic_prefix == "myswarm"


@pytest.mark.unit
class TestOpenAIConfig:
    """Test cases for OpenAIConfig."""
    
    def test_default_openai_config(self):
        """Test default OpenAI config."""
        config = OpenAIConfig()
        assert config.model == "gpt-4"
        assert config.max_tokens == 2000
        assert config.temperature == 0.7
    
    def test_openai_from_env(self, monkeypatch):
        """Test OpenAI config from environment."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
        monkeypatch.setenv("OPENAI_MAX_TOKENS", "1000")
        
        config = OpenAIConfig.from_env()
        assert config.api_key == "test-key-123"
        assert config.model == "gpt-3.5-turbo"
        assert config.max_tokens == 1000


@pytest.mark.unit
class TestAgentConfig:
    """Test cases for AgentConfig."""
    
    def test_agent_config_creation(self):
        """Test agent config creation."""
        config = AgentConfig(
            name="test_agent",
            agent_type="ContentAgent",
            domain_expertise=["content", "writing"],
        )
        assert config.name == "test_agent"
        assert config.agent_type == "ContentAgent"
        assert "content" in config.domain_expertise
    
    def test_agent_config_defaults(self):
        """Test agent config default values."""
        config = AgentConfig(
            name="test_agent",
            agent_type="BaseAgent",
        )
        assert config.confidence_threshold == 0.7
        assert config.confidence_weight == 1.0
        assert config.max_concurrent_tasks == 3
        assert config.domain_expertise == []
    
    def test_agent_config_to_dict(self):
        """Test agent config to dictionary."""
        config = AgentConfig(
            name="test_agent",
            agent_type="CodeAgent",
            domain_expertise=["code", "security"],
        )
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict["name"] == "test_agent"
        assert config_dict["agent_type"] == "CodeAgent"


@pytest.mark.integration
class TestConfigIntegration:
    """Integration tests for configuration."""
    
    def test_full_swarm_config_with_all_components(self):
        """Test creating complete swarm config with all components."""
        config = SwarmConfig(
            name="FullSwarm",
            monitoring=MonitoringConfig(
                prometheus_enabled=True,
                opentelemetry_enabled=True,
            ),
            redis=RedisConfig(
                enabled=True,
                host="redis.local",
            ),
            mqtt=MQTTConfig(
                enabled=True,
                broker_host="mqtt.local",
            ),
            openai=OpenAIConfig(
                model="gpt-4",
            ),
        )
        
        assert config.name == "FullSwarm"
        assert config.monitoring.prometheus_enabled is True
        assert config.redis.enabled is True
        assert config.mqtt.enabled is True
        assert config.openai.model == "gpt-4"
    
    def test_config_serialization(self):
        """Test full config serialization."""
        config = SwarmConfig(name="SerializeTest")
        config_dict = config.to_dict()
        
        # Ensure all required fields are present
        assert "name" in config_dict
        assert "voting_method" in config_dict
        assert "consensus_algorithm" in config_dict
        assert "monitoring" in config_dict
        assert "redis" in config_dict
        assert "mqtt" in config_dict
        assert "openai" in config_dict
