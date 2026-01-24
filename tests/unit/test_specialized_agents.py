"""Tests for specialized agents."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from pydantic_ai_swarm.agents.specialized import (
    ContentAgent,
    SocialMediaAgent,
    CodeAgent,
    SecurityAgent,
    TestingAgent,
)


@pytest.mark.unit
@pytest.mark.asyncio
class TestContentAgent:
    """Test cases for ContentAgent."""
    
    async def test_content_agent_creation(self):
        """Test content agent can be created."""
        agent = ContentAgent("test_content_agent")
        assert agent.agent_name == "test_content_agent"
        assert "content_creation" in agent.domain_expertise
        assert "writing" in agent.domain_expertise
    
    async def test_confidence_calculation_high(self):
        """Test confidence calculation for content tasks."""
        agent = ContentAgent("test_agent")
        
        task = "Write a blog post about AI"
        context = {
            "domain": "content_creation",
            "content_type": "blog_post",
        }
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence > 0.7
    
    async def test_confidence_calculation_low(self):
        """Test low confidence for non-content tasks."""
        agent = ContentAgent("test_agent")
        
        task = "Deploy a Kubernetes cluster"
        context = {"domain": "devops"}
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence < 0.5
    
    async def test_execute_content_task_success(self):
        """Test successful content task execution."""
        agent = ContentAgent("test_agent")
        
        task = "Create a blog post about Python"
        context = {
            "domain": "content_creation",
            "target_audience": "developers",
            "tone": "technical",
            "length": "medium",
        }
        
        result = await agent.execute_task(task, context)
        assert result.success
        assert result.confidence_score > 0.0
        assert "content" in result.data
        assert "metadata" in result.data
    
    async def test_execute_task_low_confidence(self):
        """Test task execution with low confidence."""
        agent = ContentAgent("test_agent")
        
        task = "Perform security audit"
        context = {"domain": "security"}
        
        result = await agent.execute_task(task, context)
        assert not result.success
        assert "Low confidence" in result.error


@pytest.mark.unit
@pytest.mark.asyncio
class TestSocialMediaAgent:
    """Test cases for SocialMediaAgent."""
    
    async def test_social_media_agent_creation(self):
        """Test social media agent can be created."""
        agent = SocialMediaAgent("test_social_agent")
        assert agent.agent_name == "test_social_agent"
        assert "social_media" in agent.domain_expertise
        assert "twitter" in agent.platforms
    
    async def test_confidence_for_social_tasks(self):
        """Test confidence for social media tasks."""
        agent = SocialMediaAgent("test_agent")
        
        task = "Create a viral TikTok post"
        context = {"platform": "tiktok"}
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence > 0.7
    
    async def test_execute_social_task(self):
        """Test social media task execution."""
        agent = SocialMediaAgent("test_agent")
        
        task = "Create a Twitter thread"
        context = {
            "platform": "twitter",
            "goal": "engagement",
        }
        
        result = await agent.execute_task(task, context)
        assert result.success
        assert result.data["platform"] == "twitter"
        assert "character_limit" in result.data["metadata"]


@pytest.mark.unit
@pytest.mark.asyncio
class TestCodeAgent:
    """Test cases for CodeAgent."""
    
    async def test_code_agent_creation(self):
        """Test code agent can be created."""
        agent = CodeAgent("test_code_agent")
        assert agent.agent_name == "test_code_agent"
        assert "code_analysis" in agent.domain_expertise
        assert "python" in agent.supported_languages
    
    async def test_confidence_for_code_tasks(self):
        """Test confidence for code-related tasks."""
        agent = CodeAgent("test_agent")
        
        task = "Review Python code for bugs"
        context = {
            "domain": "code_review",
            "language": "python",
        }
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence > 0.7
    
    async def test_execute_code_analysis(self):
        """Test code analysis task execution."""
        agent = CodeAgent("test_agent")
        
        task = "Analyze code quality"
        context = {
            "language": "python",
            "code": "def hello():\n    print('hello')",
            "focus": "quality",
        }
        
        result = await agent.execute_task(task, context)
        assert result.success
        assert "findings" in result.data
        assert "metrics" in result.data
        assert "recommendations" in result.data
    
    async def test_code_metrics_calculation(self):
        """Test code metrics calculation."""
        agent = CodeAgent("test_agent")
        
        code = """
def test():
    # This is a comment
    print("hello")
    
    return True
"""
        metrics = agent._calculate_metrics(code)
        assert "total_lines" in metrics
        assert "code_lines" in metrics
        assert "comment_lines" in metrics


@pytest.mark.unit
@pytest.mark.asyncio
class TestSecurityAgent:
    """Test cases for SecurityAgent."""
    
    async def test_security_agent_creation(self):
        """Test security agent can be created."""
        agent = SecurityAgent("test_security_agent")
        assert agent.agent_name == "test_security_agent"
        assert "security" in agent.domain_expertise
        assert "sql_injection" in agent.vulnerability_types
    
    async def test_confidence_for_security_tasks(self):
        """Test confidence for security tasks."""
        agent = SecurityAgent("test_agent")
        
        task = "Scan for vulnerabilities"
        context = {"domain": "security"}
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence > 0.7
    
    async def test_execute_security_analysis(self):
        """Test security analysis execution."""
        agent = SecurityAgent("test_agent")
        
        task = "Check for security vulnerabilities"
        context = {
            "focus": "general",
            "severity": "medium",
        }
        
        result = await agent.execute_task(task, context)
        assert result.success
        assert "vulnerabilities" in result.data
        assert "risk_score" in result.data
        assert "recommendations" in result.data


@pytest.mark.unit
@pytest.mark.asyncio
class TestTestingAgent:
    """Test cases for TestingAgent."""
    
    async def test_testing_agent_creation(self):
        """Test testing agent can be created."""
        agent = TestingAgent("test_testing_agent")
        assert agent.agent_name == "test_testing_agent"
        assert "testing" in agent.domain_expertise
    
    async def test_confidence_for_testing_tasks(self):
        """Test confidence for testing tasks."""
        agent = TestingAgent("test_agent")
        
        task = "Generate unit tests"
        context = {"domain": "testing", "test_type": "unit"}
        
        confidence = await agent.calculate_task_confidence(task, context)
        assert confidence > 0.7
    
    async def test_execute_testing_task(self):
        """Test testing task execution."""
        agent = TestingAgent("test_agent")
        
        task = "Analyze test coverage"
        context = {"test_type": "unit"}
        
        result = await agent.execute_task(task, context)
        assert result.success
        assert "test_cases" in result.data
        assert "coverage_analysis" in result.data
        assert "recommendations" in result.data
    
    async def test_test_case_generation(self):
        """Test test case generation."""
        agent = TestingAgent("test_agent")
        
        test_cases = agent._generate_test_cases("test function", "unit")
        assert len(test_cases) > 0
        assert "name" in test_cases[0]
        assert "description" in test_cases[0]


@pytest.mark.integration
@pytest.mark.asyncio
class TestAgentIntegration:
    """Integration tests for agent interactions."""
    
    async def test_multiple_agents_confidence(self):
        """Test confidence calculations across multiple agents."""
        content_agent = ContentAgent("content")
        code_agent = CodeAgent("code")
        
        task = "Write documentation for Python code"
        context = {"domain": "documentation", "language": "python"}
        
        content_confidence = await content_agent.calculate_task_confidence(task, context)
        code_confidence = await code_agent.calculate_task_confidence(task, context)
        
        # Both should have reasonable confidence
        assert content_confidence > 0.5
        assert code_confidence > 0.5
    
    async def test_agent_specialization(self):
        """Test that agents specialize correctly."""
        agents = [
            ContentAgent("content"),
            CodeAgent("code"),
            SecurityAgent("security"),
        ]
        
        task = "Review code for security issues"
        context = {"domain": "security", "language": "python"}
        
        confidences = []
        for agent in agents:
            conf = await agent.calculate_task_confidence(task, context)
            confidences.append((agent.agent_name, conf))
        
        # Security agent should have highest confidence
        confidences.sort(key=lambda x: x[1], reverse=True)
        assert confidences[0][0] == "security"
