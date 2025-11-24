# core/context.py
"""
Shared Context System for Agent Communication

Provides thread-safe shared context for agent-to-agent communication
within a single analysis session.

Usage:
    context = SharedContext()
    context.set("raw_data", data)
    anomalies = context.get("anomalies")
    context.update("metadata", {"phase": "analysis"})
"""

import asyncio
from typing import Any, Dict, Optional
from datetime import datetime


class SharedContext:
    """
    Thread-safe shared context for multi-agent communication.
    
    Stores intermediate results and data that need to be shared
    between Coordinator and sub-agents (AnalystAgent, RecommendationAgent).
    
    All operations are async-safe using asyncio locks.
    """
    
    def __init__(self):
        """Initialize shared context with empty state."""
        self._data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._created_at = datetime.now().isoformat()
        self._updated_at = self._created_at
    
    async def set(self, key: str, value: Any) -> None:
        """
        Set a value in shared context.
        
        Args:
            key: Context key
            value: Value to store (any JSON-serializable object)
        """
        async with self._lock:
            self._data[key] = value
            self._updated_at = datetime.now().isoformat()
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from shared context.
        
        Args:
            key: Context key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        async with self._lock:
            return self._data.get(key, default)
    
    async def update(self, key: str, partial_value: Dict[str, Any]) -> None:
        """
        Update a dictionary value in context (merge operation).
        
        Args:
            key: Context key (must contain a dict)
            partial_value: Dictionary to merge with existing value
        """
        async with self._lock:
            if key not in self._data:
                self._data[key] = {}
            
            if isinstance(self._data[key], dict) and isinstance(partial_value, dict):
                self._data[key].update(partial_value)
                self._updated_at = datetime.now().isoformat()
            else:
                raise ValueError(f"Key '{key}' must contain a dictionary for update operation")
    
    async def clear(self) -> None:
        """Clear all data from context."""
        async with self._lock:
            self._data.clear()
            self._updated_at = datetime.now().isoformat()
    
    async def list_keys(self) -> list:
        """
        List all keys in context.
        
        Returns:
            List of all keys currently stored
        """
        async with self._lock:
            return list(self._data.keys())
    
    async def to_dict(self) -> Dict[str, Any]:
        """
        Export entire context as dictionary.
        
        Returns:
            Copy of all stored data with metadata
        """
        async with self._lock:
            return {
                "data": self._data.copy(),
                "created_at": self._created_at,
                "updated_at": self._updated_at
            }
