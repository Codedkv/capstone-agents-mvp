# tools/base_tool.py
"""
Base Tool Classes for Agent System

Provides base classes and data structures for all tools.
"""

from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ToolParameter:
    """Tool parameter specification."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


@dataclass
class ToolResult:
    """Standardized tool execution result."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


class ToolExecutionError(Exception):
    """Custom exception for tool execution failures."""
    pass


class BaseTool:
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    async def execute(self, *args, **kwargs):
        """Execute tool logic. Must be implemented in subclass."""
        raise NotImplementedError("Must be implemented in subclass")
