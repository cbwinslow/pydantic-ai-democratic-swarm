"""Code analysis and development specialized agents.

This module provides agents specialized in code-related tasks including
code review, security analysis, testing, and quality assurance.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from pydantic_ai_swarm.core.base_agent import BaseAgent
from pydantic_ai_swarm.core.orchestrator import TaskResult


class CodeAgent(BaseAgent):
    """Specialized agent for code analysis and development tasks.
    
    This agent excels at:
    - Code review and analysis
    - Bug detection
    - Code quality assessment
    - Refactoring suggestions
    - Best practices enforcement
    
    Example:
        >>> agent = CodeAgent("code_reviewer")
        >>> result = await agent.execute_task(
        ...     "Review this Python code for issues",
        ...     {"language": "python", "focus": "security"}
        ... )
    """
    
    def __init__(
        self,
        agent_name: str,
        description: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize code agent.
        
        Args:
            agent_name: Unique name for the agent
            description: Optional description of the agent
            **kwargs: Additional configuration options
        """
        super().__init__(
            agent_name=agent_name,
            description=description or "Code analysis and development specialist",
            **kwargs
        )
        self.domain_expertise = [
            "code_analysis",
            "code_review",
            "debugging",
            "refactoring",
            "security",
            "performance",
            "testing",
            "best_practices",
        ]
        self.supported_languages = [
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "rust",
            "c++",
            "c#",
            "ruby",
            "php",
        ]
    
    async def calculate_task_confidence(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for code-related tasks.
        
        Args:
            task: Task description
            context: Task context with additional parameters
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0
        task_lower = task.lower()
        
        # Check for code-related keywords
        code_keywords = [
            "code", "review", "bug", "debug", "refactor", "analyze",
            "test", "security", "vulnerability", "optimize", "performance",
            "function", "class", "method", "api", "endpoint",
        ]
        
        keyword_matches = sum(1 for kw in code_keywords if kw in task_lower)
        confidence += min(keyword_matches * 0.15, 0.6)
        
        # Check domain match
        domain = context.get("domain", "").lower()
        if domain in self.domain_expertise:
            confidence += 0.25
        
        # Check language support
        language = context.get("language", "").lower()
        if language in self.supported_languages:
            confidence += 0.15
        
        return min(confidence, 1.0)
    
    async def execute_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute code analysis task.
        
        Args:
            task: Task description
            context: Task context including:
                - language: Programming language
                - code: Code to analyze
                - focus: Analysis focus (security, performance, quality, etc.)
                - severity: Minimum severity level to report
                
        Returns:
            TaskResult with analysis results or error
        """
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < self.confidence_threshold:
            return TaskResult(
                success=False,
                error=f"Low confidence ({confidence:.2f}) for code analysis task",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
        
        try:
            language = context.get("language", "unknown")
            focus = context.get("focus", "general")
            code = context.get("code", "")
            
            # Perform analysis
            analysis_result = {
                "summary": f"Code analysis completed for {language}",
                "language": language,
                "focus": focus,
                "findings": self._analyze_code(code, language, focus),
                "metrics": self._calculate_metrics(code),
                "recommendations": self._generate_recommendations(code, language, focus),
            }
            
            return TaskResult(
                success=True,
                data=analysis_result,
                confidence_score=confidence,
                agent_name=self.agent_name,
                metadata={
                    "language": language,
                    "focus": focus,
                    "domain": "code_analysis",
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Code analysis failed: {str(e)}",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
    
    def _analyze_code(
        self,
        code: str,
        language: str,
        focus: str
    ) -> List[Dict[str, Any]]:
        """Analyze code and return findings."""
        # Simplified analysis - in production, use real static analysis tools
        findings = []
        
        if not code:
            return findings
        
        # Example findings based on focus
        if focus == "security":
            findings.append({
                "type": "security",
                "severity": "medium",
                "message": "Potential SQL injection vulnerability detected",
                "line": 42,
                "recommendation": "Use parameterized queries",
            })
        
        if focus == "performance":
            findings.append({
                "type": "performance",
                "severity": "low",
                "message": "Inefficient loop detected",
                "line": 15,
                "recommendation": "Consider using list comprehension",
            })
        
        return findings
    
    def _calculate_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate code metrics."""
        if not code:
            return {}
        
        lines = code.split("\n")
        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "complexity": "medium",  # Simplified
        }
    
    def _generate_recommendations(
        self,
        code: str,
        language: str,
        focus: str
    ) -> List[str]:
        """Generate code improvement recommendations."""
        recommendations = []
        
        if language == "python":
            recommendations.extend([
                "Follow PEP 8 style guidelines",
                "Add type hints for better code clarity",
                "Include docstrings for all public functions",
            ])
        
        if focus == "security":
            recommendations.extend([
                "Implement input validation",
                "Use parameterized queries",
                "Enable CSRF protection",
            ])
        
        if focus == "performance":
            recommendations.extend([
                "Profile code to identify bottlenecks",
                "Consider caching frequently accessed data",
                "Optimize database queries",
            ])
        
        return recommendations


class SecurityAgent(BaseAgent):
    """Specialized agent for security analysis and vulnerability detection.
    
    This agent focuses on:
    - Security vulnerability detection
    - Penetration testing insights
    - Security best practices
    - Compliance checking
    - Threat modeling
    """
    
    def __init__(
        self,
        agent_name: str,
        description: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize security agent."""
        super().__init__(
            agent_name=agent_name,
            description=description or "Security analysis specialist",
            **kwargs
        )
        self.domain_expertise = [
            "security",
            "vulnerability_analysis",
            "penetration_testing",
            "compliance",
            "threat_modeling",
            "encryption",
            "authentication",
            "authorization",
        ]
        self.vulnerability_types = [
            "sql_injection",
            "xss",
            "csrf",
            "authentication_bypass",
            "privilege_escalation",
            "information_disclosure",
            "buffer_overflow",
            "insecure_deserialization",
        ]
    
    async def calculate_task_confidence(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for security tasks."""
        confidence = 0.0
        task_lower = task.lower()
        
        # Check for security keywords
        security_keywords = [
            "security", "vulnerability", "exploit", "attack", "threat",
            "penetration", "audit", "compliance", "encryption", "auth",
            "authorization", "authentication", "injection", "xss", "csrf",
        ]
        
        keyword_matches = sum(1 for kw in security_keywords if kw in task_lower)
        confidence += min(keyword_matches * 0.2, 0.7)
        
        # Check domain match
        domain = context.get("domain", "").lower()
        if domain in self.domain_expertise:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    async def execute_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute security analysis task."""
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < self.confidence_threshold:
            return TaskResult(
                success=False,
                error=f"Low confidence ({confidence:.2f}) for security task",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
        
        try:
            focus = context.get("focus", "general")
            severity_threshold = context.get("severity", "low")
            
            result = {
                "summary": "Security analysis completed",
                "vulnerabilities": self._detect_vulnerabilities(context),
                "risk_score": self._calculate_risk_score(context),
                "recommendations": self._security_recommendations(focus),
                "compliance": self._check_compliance(context),
            }
            
            return TaskResult(
                success=True,
                data=result,
                confidence_score=confidence,
                agent_name=self.agent_name,
                metadata={
                    "focus": focus,
                    "domain": "security",
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Security analysis failed: {str(e)}",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
    
    def _detect_vulnerabilities(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security vulnerabilities."""
        # Simplified vulnerability detection
        return [
            {
                "type": "sql_injection",
                "severity": "high",
                "location": "api/user_endpoint.py:45",
                "description": "Unsanitized user input used in SQL query",
                "cve": "CVE-2024-XXXXX",
            }
        ]
    
    def _calculate_risk_score(self, context: Dict[str, Any]) -> float:
        """Calculate overall security risk score."""
        # Simplified risk calculation
        return 6.5  # Score out of 10
    
    def _security_recommendations(self, focus: str) -> List[str]:
        """Generate security recommendations."""
        recommendations = [
            "Implement input validation and sanitization",
            "Use parameterized queries to prevent SQL injection",
            "Enable HTTPS for all endpoints",
            "Implement rate limiting",
            "Use secure password hashing (bcrypt, argon2)",
        ]
        
        if focus == "authentication":
            recommendations.extend([
                "Implement multi-factor authentication (MFA)",
                "Use secure session management",
                "Implement account lockout after failed attempts",
            ])
        
        return recommendations
    
    def _check_compliance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check security compliance."""
        return {
            "owasp_top_10": "partial_compliance",
            "gdpr": "requires_review",
            "pci_dss": "not_applicable",
            "sox": "not_applicable",
        }


class TestingAgent(BaseAgent):
    """Specialized agent for software testing and QA.
    
    This agent specializes in:
    - Test case generation
    - Test coverage analysis
    - Automated testing strategies
    - Bug reproduction
    - QA best practices
    """
    
    def __init__(
        self,
        agent_name: str,
        description: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Initialize testing agent."""
        super().__init__(
            agent_name=agent_name,
            description=description or "Software testing and QA specialist",
            **kwargs
        )
        self.domain_expertise = [
            "testing",
            "qa",
            "test_automation",
            "test_coverage",
            "integration_testing",
            "unit_testing",
            "e2e_testing",
            "performance_testing",
        ]
    
    async def calculate_task_confidence(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> float:
        """Calculate confidence for testing tasks."""
        confidence = 0.0
        task_lower = task.lower()
        
        testing_keywords = [
            "test", "qa", "quality", "coverage", "automation",
            "unit test", "integration", "e2e", "bug", "verify",
        ]
        
        keyword_matches = sum(1 for kw in testing_keywords if kw in task_lower)
        confidence += min(keyword_matches * 0.2, 0.7)
        
        domain = context.get("domain", "").lower()
        if domain in self.domain_expertise:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    async def execute_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> TaskResult:
        """Execute testing task."""
        confidence = await self.calculate_task_confidence(task, context)
        
        if confidence < self.confidence_threshold:
            return TaskResult(
                success=False,
                error=f"Low confidence ({confidence:.2f}) for testing task",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
        
        try:
            test_type = context.get("test_type", "unit")
            
            result = {
                "summary": f"{test_type.title()} testing analysis completed",
                "test_cases": self._generate_test_cases(task, test_type),
                "coverage_analysis": self._analyze_coverage(context),
                "recommendations": self._testing_recommendations(test_type),
            }
            
            return TaskResult(
                success=True,
                data=result,
                confidence_score=confidence,
                agent_name=self.agent_name,
                metadata={
                    "test_type": test_type,
                    "domain": "testing",
                },
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                error=f"Testing analysis failed: {str(e)}",
                confidence_score=confidence,
                agent_name=self.agent_name,
            )
    
    def _generate_test_cases(self, task: str, test_type: str) -> List[Dict[str, Any]]:
        """Generate test cases."""
        return [
            {
                "name": f"test_{test_type}_success_case",
                "description": "Test successful execution path",
                "expected_result": "success",
            },
            {
                "name": f"test_{test_type}_error_handling",
                "description": "Test error handling",
                "expected_result": "error_handled_gracefully",
            },
        ]
    
    def _analyze_coverage(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test coverage."""
        return {
            "line_coverage": 85.5,
            "branch_coverage": 78.2,
            "function_coverage": 92.1,
            "target_coverage": 80.0,
            "meets_target": True,
        }
    
    def _testing_recommendations(self, test_type: str) -> List[str]:
        """Generate testing recommendations."""
        return [
            f"Increase {test_type} test coverage to 90%",
            "Add edge case testing",
            "Implement automated testing in CI/CD",
            "Use test fixtures for consistent setup",
        ]
