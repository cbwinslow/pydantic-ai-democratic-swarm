"""Content creation specialized agent.

This agent specializes in content creation tasks including writing,
editing, and content strategy.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from pydantic_ai_swarm.core.base_agent import BaseAgent
from pydantic_ai_swarm.core.orchestrator import TaskResult


class ContentAgent(BaseAgent):
    """Specialized agent for content creation and writing tasks.
    
    This agent excels at:
    - Blog posts and articles
    - Social media content
    - Marketing copy
    - Documentation
    - Creative writing
    
    Example:
        >>> agent = ContentAgent("content_writer")
        >>> result = await agent.execute_task(
        ...     "Write a blog post about AI",
        ...     {"target_audience": "developers", "length": "medium"}
        ... )
    """
    
    def __init__(
        self,
        agent_name: str,
        **kwargs: Any
    ) -> None:
        """Initialize content agent.
        
        Args:
            agent_name: Unique name for the agent
            **kwargs: Additional configuration options
        """
        super().__init__(agent_name=agent_name, **kwargs)
        self.domain_expertise = [
            "content_creation",
            "writing",
            "editing",
            "blogging",
            "social_media",
            "marketing",
            "documentation",
        ]
        self.content_types = [
            "blog_post",
            "article",
            "social_media_post",
            "marketing_copy",
            "technical_documentation",
            "creative_writing",
            "email",
            "press_release",
        ]
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize content-specific tools.
        
        Returns:
            Dictionary of tools for content creation
        """
        # In a full implementation, this would return actual tool instances
        return {}
    
    async def calculate_task_confidence(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for content creation tasks.
        
        Args:
            task: Task description
            context: Task context with additional parameters
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0
        task_lower = task.lower()
        
        # Check for content creation keywords
        content_keywords = [
            "write", "create", "blog", "article", "post", "content",
            "copy", "social media", "tweet", "linkedin", "facebook",
            "documentation", "doc", "guide", "tutorial", "story",
        ]
        
        keyword_matches = sum(1 for kw in content_keywords if kw in task_lower)
        confidence += min(keyword_matches * 0.15, 0.6)
        
        # Check domain match
        domain = context.get("domain", "").lower()
        if domain in self.domain_expertise:
            confidence += 0.25
        
        # Check content type
        content_type = context.get("content_type", "").lower()
        if content_type in self.content_types:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    async def execute_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute content creation task.
        
        Args:
            task: Task description
            context: Task context including:
                - target_audience: Target audience for content
                - tone: Writing tone (formal, casual, technical, etc.)
                - length: Content length (short, medium, long)
                - keywords: SEO keywords to include
                - format: Output format
                
        Returns:
            TaskResult with created content or error
        """
        # Calculate confidence first
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < self.confidence_threshold:
            return TaskResult(
                success=False,
                error=f"Low confidence ({confidence:.2f}) for content task",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
        
        try:
            # Extract context parameters
            target_audience = context.get("target_audience", "general")
            tone = context.get("tone", "professional")
            length = context.get("length", "medium")
            keywords = context.get("keywords", [])
            
            # Simulate content creation
            # In a real implementation, this would use an LLM API
            content_result = {
                "content": f"[Content created for: {task}]",
                "metadata": {
                    "target_audience": target_audience,
                    "tone": tone,
                    "length": length,
                    "keywords": keywords,
                    "word_count": self._estimate_word_count(length),
                },
                "suggestions": self._generate_suggestions(task, context),
            }
            
            return TaskResult(
                success=True,
                data=content_result,
                confidence_score=confidence,
                agent_name=self.agent_name,
                metadata={
                    "content_type": context.get("content_type", "general"),
                    "domain": "content_creation",
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Content creation failed: {str(e)}",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
    
    def _estimate_word_count(self, length: str) -> int:
        """Estimate word count based on length specification."""
        length_map = {
            "short": 300,
            "medium": 800,
            "long": 1500,
            "very_long": 2500,
        }
        return length_map.get(length.lower(), 800)
    
    def _generate_suggestions(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate content improvement suggestions."""
        suggestions = []
        
        # Check for SEO keywords
        if not context.get("keywords"):
            suggestions.append("Consider adding SEO keywords for better discoverability")
        
        # Check for target audience
        if not context.get("target_audience"):
            suggestions.append("Define target audience for more focused content")
        
        # Check for tone
        if not context.get("tone"):
            suggestions.append("Specify writing tone for consistent voice")
        
        return suggestions


class SocialMediaAgent(BaseAgent):
    """Specialized agent for social media content creation.
    
    This agent specializes in:
    - Platform-specific content (Twitter/X, LinkedIn, Instagram, Facebook, TikTok)
    - Hashtag optimization
    - Engagement strategies
    - Content calendars
    - Viral content creation
    """
    
    def __init__(
        self,
        agent_name: str,
        **kwargs: Any
    ) -> None:
        """Initialize social media agent."""
        super().__init__(agent_name=agent_name, **kwargs)
        self.domain_expertise = [
            "social_media",
            "twitter",
            "linkedin",
            "instagram",
            "facebook",
            "tiktok",
            "engagement",
            "viral_marketing",
        ]
        self.platforms = ["twitter", "linkedin", "instagram", "facebook", "tiktok", "youtube"]
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize social media-specific tools.
        
        Returns:
            Dictionary of tools for social media
        """
        return {}
    
    async def calculate_task_confidence(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for social media tasks."""
        confidence = 0.0
        task_lower = task.lower()
        
        # Check for social media keywords
        social_keywords = [
            "tweet", "post", "share", "social", "viral", "engagement",
            "hashtag", "instagram", "linkedin", "facebook", "tiktok",
        ]
        
        keyword_matches = sum(1 for kw in social_keywords if kw in task_lower)
        confidence += min(keyword_matches * 0.2, 0.7)
        
        # Check platform specification
        platform = context.get("platform", "").lower()
        if platform in self.platforms:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    async def execute_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute social media content creation task."""
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < self.confidence_threshold:
            return TaskResult(
                success=False,
                error=f"Low confidence ({confidence:.2f}) for social media task",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
        
        try:
            platform = context.get("platform", "general")
            goal = context.get("goal", "engagement")
            
            result = {
                "content": f"[Social media content for: {task}]",
                "platform": platform,
                "metadata": {
                    "goal": goal,
                    "character_limit": self._get_character_limit(platform),
                    "optimal_hashtags": self._suggest_hashtags(task, platform),
                    "best_posting_time": self._suggest_posting_time(platform),
                },
            }
            
            return TaskResult(
                success=True,
                data=result,
                confidence_score=confidence,
                agent_name=self.agent_name,
                metadata={"platform": platform, "domain": "social_media"},
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Social media content creation failed: {str(e)}",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
    
    def _get_character_limit(self, platform: str) -> Optional[int]:
        """Get character limit for platform."""
        limits = {
            "twitter": 280,
            "linkedin": 3000,
            "instagram": 2200,
            "facebook": 63206,
            "tiktok": 150,
        }
        return limits.get(platform.lower())
    
    def _suggest_hashtags(self, task: str, platform: str) -> List[str]:
        """Suggest relevant hashtags."""
        # Simplified hashtag suggestion
        return ["#AI", "#Tech", "#Innovation"]
    
    def _suggest_posting_time(self, platform: str) -> str:
        """Suggest optimal posting time."""
        times = {
            "twitter": "9 AM - 3 PM EST weekdays",
            "linkedin": "7-8 AM, 12 PM, 5-6 PM EST weekdays",
            "instagram": "11 AM - 1 PM EST",
            "facebook": "1-4 PM EST",
            "tiktok": "6-10 PM EST",
        }
        return times.get(platform.lower(), "9 AM - 5 PM EST")
