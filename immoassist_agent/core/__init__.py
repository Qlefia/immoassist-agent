"""
Core module for ImmoAssist multi-agent system.

This module contains the foundational components following clean architecture principles:
- Domain models and protocols
- Configuration management
- Custom exceptions
- Core interfaces and abstractions
"""

from .config import ImmoAssistConfig
from .exceptions import (
    ImmoAssistError,
    SessionError,
    AgentError,
    ToolError,
    ValidationError,
    ConfigurationError,
    RagError,
    IntegrationError,
    RateLimitError,
    SecurityError,
)
from .protocols import (
    AgentProtocol,
    SessionManagerProtocol,
    ToolProtocol,
    LoggerProtocol,
    ConfigProtocol,
)
from .models import (
    SessionState,
    UserProfile,
    CalculationResult,
    PropertySearchResult,
    MarketAnalysisResult,
    Language,
    ExperienceLevel,
    PropertyType,
    CalculationType,
    PropertyDetails,
    PropertySearchCriteria,
    AgentResponse,
    ToolExecutionResult,
)
from .logging import (
    ImmoAssistLogger,
    get_logger,
    correlation_context,
    time_operation,
    correlation_id,
)

__all__ = [
    # Configuration
    "ImmoAssistConfig",
    # Exceptions
    "ImmoAssistError",
    "SessionError", 
    "AgentError",
    "ToolError",
    "ValidationError",
    "ConfigurationError",
    "RagError",
    "IntegrationError", 
    "RateLimitError",
    "SecurityError",
    # Protocols
    "AgentProtocol",
    "SessionManagerProtocol",
    "ToolProtocol",
    "LoggerProtocol",
    "ConfigProtocol",
    # Models
    "SessionState",
    "UserProfile",
    "CalculationResult",
    "PropertySearchResult",
    "MarketAnalysisResult",
    "Language",
    "ExperienceLevel",
    "PropertyType",
    "CalculationType",
    "PropertyDetails",
    "PropertySearchCriteria",
    "AgentResponse",
    "ToolExecutionResult",
    # Logging
    "ImmoAssistLogger",
    "get_logger",
    "correlation_context",
    "time_operation",
    "correlation_id",
] 