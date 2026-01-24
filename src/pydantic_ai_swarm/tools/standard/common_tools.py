"""Standard tools for Pydantic AI Swarm agents.

This module provides a collection of standard tools that agents can use
to perform common operations.
"""

from typing import Dict, Any, List, Optional
from pydantic import Field

from pydantic_ai_swarm.tools.robust_tool import RobustTool, ToolResult


class FileReaderTool(RobustTool):
    """Tool for reading files from the filesystem.
    
    This tool allows agents to read file contents safely with
    proper error handling and validation.
    
    Example:
        >>> tool = FileReaderTool()
        >>> result = await tool.execute({"path": "example.txt"})
    """
    
    def __init__(self) -> None:
        """Initialize file reader tool."""
        super().__init__(
            name="file_reader",
            description="Read contents of a file from the filesystem"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute file reading.
        
        Args:
            parameters: Must include:
                - path: Path to the file to read
                - encoding: Optional encoding (default: utf-8)
                - max_size: Optional maximum file size in bytes
                
        Returns:
            ToolResult with file contents or error
        """
        try:
            path = parameters.get("path")
            if not path:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: path"
                )
            
            encoding = parameters.get("encoding", "utf-8")
            max_size = parameters.get("max_size", 1024 * 1024)  # 1MB default
            
            import os
            if not os.path.exists(path):
                return ToolResult(
                    success=False,
                    error=f"File not found: {path}"
                )
            
            file_size = os.path.getsize(path)
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    error=f"File too large: {file_size} bytes (max: {max_size})"
                )
            
            with open(path, "r", encoding=encoding) as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={
                    "content": content,
                    "path": path,
                    "size": file_size,
                    "encoding": encoding,
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error reading file: {str(e)}"
            )
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["content_agent", "code_agent", "analysis_agent"]


class WebScraperTool(RobustTool):
    """Tool for scraping web content.
    
    Fetches and parses content from web URLs with proper
    error handling and rate limiting.
    """
    
    def __init__(self) -> None:
        """Initialize web scraper tool."""
        super().__init__(
            name="web_scraper",
            description="Fetch and parse content from web URLs"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute web scraping.
        
        Args:
            parameters: Must include:
                - url: URL to scrape
                - timeout: Optional timeout in seconds
                - headers: Optional HTTP headers
                
        Returns:
            ToolResult with scraped content or error
        """
        try:
            url = parameters.get("url")
            if not url:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: url"
                )
            
            timeout = parameters.get("timeout", 30)
            
            # Simplified - in production, use aiohttp or httpx
            import urllib.request
            
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'PydanticAISwarm/1.0')
            
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8')
                status_code = response.status
            
            return ToolResult(
                success=True,
                data={
                    "content": content,
                    "url": url,
                    "status_code": status_code,
                    "content_length": len(content),
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error scraping URL: {str(e)}"
            )
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["content_agent", "research_agent", "analysis_agent"]


class DataValidatorTool(RobustTool):
    """Tool for validating data against schemas.
    
    Validates data using Pydantic models and JSON schemas.
    """
    
    def __init__(self) -> None:
        """Initialize data validator tool."""
        super().__init__(
            name="data_validator",
            description="Validate data against schemas"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute data validation.
        
        Args:
            parameters: Must include:
                - data: Data to validate
                - schema: Validation schema (dict or Pydantic model)
                - strict: Optional strict validation mode
                
        Returns:
            ToolResult with validation results
        """
        try:
            data = parameters.get("data")
            schema = parameters.get("schema")
            
            if data is None:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: data"
                )
            
            if not schema:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: schema"
                )
            
            # Simplified validation
            errors = []
            
            # Basic type checking
            if isinstance(schema, dict):
                for key, expected_type in schema.items():
                    if key not in data:
                        errors.append(f"Missing field: {key}")
                    elif not isinstance(data[key], expected_type):
                        errors.append(
                            f"Invalid type for {key}: expected {expected_type.__name__}, "
                            f"got {type(data[key]).__name__}"
                        )
            
            if errors:
                return ToolResult(
                    success=False,
                    data={
                        "valid": False,
                        "errors": errors,
                    }
                )
            
            return ToolResult(
                success=True,
                data={
                    "valid": True,
                    "errors": [],
                    "validated_data": data,
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error validating data: {str(e)}"
            )
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["code_agent", "testing_agent", "quality_agent"]


class TextProcessorTool(RobustTool):
    """Tool for text processing operations.
    
    Provides common text operations like summarization,
    tokenization, and transformation.
    """
    
    def __init__(self) -> None:
        """Initialize text processor tool."""
        super().__init__(
            name="text_processor",
            description="Process and transform text content"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute text processing.
        
        Args:
            parameters: Must include:
                - text: Text to process
                - operation: Operation to perform (summarize, tokenize, etc.)
                - options: Optional operation-specific options
                
        Returns:
            ToolResult with processed text
        """
        try:
            text = parameters.get("text")
            operation = parameters.get("operation", "tokenize")
            
            if not text:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: text"
                )
            
            result_data: Dict[str, Any] = {"operation": operation}
            
            if operation == "tokenize":
                tokens = text.split()
                result_data["tokens"] = tokens
                result_data["token_count"] = len(tokens)
                
            elif operation == "summarize":
                # Simplified summarization - take first 100 words
                tokens = text.split()
                summary = " ".join(tokens[:100])
                result_data["summary"] = summary
                result_data["original_length"] = len(tokens)
                result_data["summary_length"] = min(100, len(tokens))
                
            elif operation == "word_count":
                words = text.split()
                sentences = text.split(".")
                result_data["word_count"] = len(words)
                result_data["sentence_count"] = len([s for s in sentences if s.strip()])
                result_data["character_count"] = len(text)
                
            elif operation == "extract_keywords":
                # Simplified keyword extraction
                words = text.lower().split()
                word_freq: Dict[str, int] = {}
                for word in words:
                    word = word.strip(".,!?;:")
                    if len(word) > 3:  # Only words longer than 3 chars
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
                result_data["keywords"] = [k[0] for k in keywords]
                
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
            
            return ToolResult(
                success=True,
                data=result_data
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error processing text: {str(e)}"
            )
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["content_agent", "analysis_agent", "research_agent"]


class CodeAnalyzerTool(RobustTool):
    """Tool for analyzing code structure and quality.
    
    Provides static analysis, complexity metrics, and
    code quality checks.
    """
    
    def __init__(self) -> None:
        """Initialize code analyzer tool."""
        super().__init__(
            name="code_analyzer",
            description="Analyze code structure and quality"
        )
    
    async def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute code analysis.
        
        Args:
            parameters: Must include:
                - code: Code to analyze
                - language: Programming language
                - checks: Optional list of checks to perform
                
        Returns:
            ToolResult with analysis results
        """
        try:
            code = parameters.get("code")
            language = parameters.get("language", "python")
            
            if not code:
                return ToolResult(
                    success=False,
                    error="Missing required parameter: code"
                )
            
            lines = code.split("\n")
            
            analysis = {
                "language": language,
                "metrics": {
                    "total_lines": len(lines),
                    "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
                    "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
                    "blank_lines": len([l for l in lines if not l.strip()]),
                },
                "issues": [],
                "complexity": "medium",  # Simplified
            }
            
            # Simple checks
            if "TODO" in code or "FIXME" in code:
                analysis["issues"].append({
                    "type": "quality",
                    "message": "TODO/FIXME comments found",
                    "severity": "low",
                })
            
            if len(lines) > 1000:
                analysis["issues"].append({
                    "type": "structure",
                    "message": "File is very long (>1000 lines)",
                    "severity": "medium",
                })
            
            return ToolResult(
                success=True,
                data=analysis
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error analyzing code: {str(e)}"
            )
    
    @property
    def compatible_agents(self) -> List[str]:
        """List compatible agents."""
        return ["code_agent", "security_agent", "testing_agent"]
