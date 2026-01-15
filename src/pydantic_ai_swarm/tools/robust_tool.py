"""Robust Tool Framework for Agent Tools.

Provides a framework for creating resilient, well-validated tools for agents.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import logging


logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """Result of a tool execution."""
    success: bool
    data: Any = None
    error: str = ""
    execution_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_id": self.execution_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class RobustTool(ABC):
    """Base class for robust agent tools with validation and fallback."""
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """Initialize robust tool.
        
        Args:
            name: Tool name
            description: Tool description
            config: Optional configuration
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.logger = logging.getLogger(f"RobustTool.{name}")
    
    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute the tool with validation and error handling.
        
        Args:
            parameters: Tool parameters
            
        Returns:
            ToolResult with execution outcome
        """
        execution_id = f"{self.name}_{datetime.now().timestamp()}"
        self.execution_count += 1
        
        try:
            # Validate parameters
            validation_error = self._validate_parameters(parameters)
            if validation_error:
                self.failure_count += 1
                return ToolResult(
                    success=False,
                    error=f"Validation error: {validation_error}",
                    execution_id=execution_id
                )
            
            # Execute core logic
            result_data = self._execute_core(parameters, execution_id)
            
            self.success_count += 1
            return ToolResult(
                success=True,
                data=result_data,
                execution_id=execution_id
            )
            
        except Exception as e:
            self.failure_count += 1
            self.logger.error(f"Tool execution failed: {e}")
            
            # Try fallback strategies
            fallback_result = self._try_fallbacks(e, parameters, execution_id)
            if fallback_result:
                return fallback_result
            
            return ToolResult(
                success=False,
                error=str(e),
                execution_id=execution_id
            )
    
    @abstractmethod
    def _execute_core(self, parameters: Dict[str, Any], execution_id: str) -> Any:
        """Core tool execution logic.
        
        Args:
            parameters: Validated parameters
            execution_id: Unique execution ID
            
        Returns:
            Tool execution result data
        """
        pass
    
    @abstractmethod
    def _define_validation_schema(self) -> Dict[str, Any]:
        """Define parameter validation schema.
        
        Returns:
            Validation schema dictionary
        """
        pass
    
    @abstractmethod
    def _define_fallback_strategies(self) -> List[Dict[str, Any]]:
        """Define fallback strategies for error handling.
        
        Returns:
            List of fallback strategy dictionaries
        """
        pass
    
    def _validate_parameters(self, parameters: Dict[str, Any]) -> Optional[str]:
        """Validate tool parameters.
        
        Args:
            parameters: Parameters to validate
            
        Returns:
            Error message if validation fails, None otherwise
        """
        schema = self._define_validation_schema()
        
        # Simple validation - check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in parameters:
                return f"Missing required parameter: {field}"
        
        return None
    
    def _try_fallbacks(
        self,
        error: Exception,
        parameters: Dict[str, Any],
        execution_id: str
    ) -> Optional[ToolResult]:
        """Try fallback strategies.
        
        Args:
            error: The error that occurred
            parameters: Original parameters
            execution_id: Execution ID
            
        Returns:
            ToolResult if fallback succeeds, None otherwise
        """
        strategies = self._define_fallback_strategies()
        
        for strategy in strategies:
            try:
                condition = strategy.get("condition")
                action = strategy.get("action")
                
                if condition and condition(error, parameters, execution_id):
                    result = action(error, parameters, execution_id)
                    if result and isinstance(result, ToolResult):
                        return result
                        
            except Exception as e:
                self.logger.warning(f"Fallback strategy failed: {e}")
                continue
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get tool execution statistics.
        
        Returns:
            Dictionary with stats
        """
        success_rate = (
            self.success_count / self.execution_count
            if self.execution_count > 0
            else 0.0
        )
        
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": success_rate
        }
    
    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
