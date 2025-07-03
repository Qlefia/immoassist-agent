"""
Protocol definitions for ImmoAssist multi-agent system.

This module defines the core protocols and interfaces that establish
contracts for different components of the system, enabling loose coupling
and following the dependency inversion principle.
"""

from typing import Protocol, runtime_checkable, Dict, Any, Optional, List
from abc import abstractmethod

from google.adk.agents import Agent
from google.adk.sessions.state import State
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext


@runtime_checkable
class LoggerProtocol(Protocol):
    """Protocol for logging implementations."""
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info level message."""
        ...
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning level message."""
        ...
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log error level message."""
        ...
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug level message."""
        ...


@runtime_checkable
class ConfigProtocol(Protocol):
    """Protocol for configuration management."""
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent."""
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary."""
        ...


@runtime_checkable  
class SessionManagerProtocol(Protocol):
    """Protocol for session management implementations."""
    
    @abstractmethod
    def initialize_session(self, callback_context: CallbackContext) -> None:
        """Initialize a new session with proper state management."""
        ...
    
    @abstractmethod
    def update_session_activity(self, state: State) -> None:
        """Update session activity timestamp and metrics."""
        ...


@runtime_checkable
class ToolProtocol(Protocol):
    """Protocol for tool implementations."""
    
    @abstractmethod
    def execute(self, parameters: str, context: ToolContext) -> Dict[str, Any]:
        """Execute the tool with given parameters and context."""
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the tool name."""
        ...


@runtime_checkable
class AgentProtocol(Protocol):
    """Protocol for agent implementations."""
    
    @abstractmethod
    def create_agent(self) -> Agent:
        """Create and configure the agent instance."""
        ...
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the agent name."""
        ... 