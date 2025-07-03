"""
Custom exceptions for ImmoAssist multi-agent system.

This module defines a comprehensive exception hierarchy that provides
clear error handling and debugging capabilities throughout the system.
Following the principle of explicit error handling.
"""

from typing import Optional, Dict, Any


class ImmoAssistError(Exception):
    """
    Base exception class for all ImmoAssist-related errors.
    
    Provides a foundation for all custom exceptions with enhanced
    error context and debugging information.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code for logging/monitoring
            context: Additional context information for debugging
            cause: The underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for structured logging.
        
        Returns:
            Dictionary representation of the exception
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
        }


class ConfigurationError(ImmoAssistError):
    """
    Raised when there are configuration-related errors.
    
    This includes missing required configuration, invalid values,
    or environment-specific configuration problems.
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        expected_value: Optional[str] = None,
        actual_value: Optional[str] = None
    ) -> None:
        context = {
            "config_key": config_key,
            "expected_value": expected_value,
            "actual_value": actual_value,
        }
        super().__init__(
            message=message,
            error_code="CONFIG_ERROR",
            context=context
        )


class SessionError(ImmoAssistError):
    """
    Raised when there are session management errors.
    
    This includes session initialization failures, state corruption,
    or session timeout issues.
    """
    
    def __init__(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        operation: Optional[str] = None
    ) -> None:
        context = {
            "session_id": session_id,
            "operation": operation,
        }
        super().__init__(
            message=message,
            error_code="SESSION_ERROR",
            context=context
        )


class AgentError(ImmoAssistError):
    """
    Raised when there are agent-related errors.
    
    This includes agent initialization failures, delegation errors,
    or agent communication problems.
    """
    
    def __init__(
        self, 
        message: str, 
        agent_name: Optional[str] = None,
        operation: Optional[str] = None,
        agent_type: Optional[str] = None
    ) -> None:
        context = {
            "agent_name": agent_name,
            "operation": operation,
            "agent_type": agent_type,
        }
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            context=context
        )


class ToolError(ImmoAssistError):
    """
    Raised when there are tool execution errors.
    
    This includes tool initialization failures, execution timeouts,
    or tool-specific errors.
    """
    
    def __init__(
        self, 
        message: str, 
        tool_name: Optional[str] = None,
        operation: Optional[str] = None,
        timeout_seconds: Optional[int] = None
    ) -> None:
        context = {
            "tool_name": tool_name,
            "operation": operation,
            "timeout_seconds": timeout_seconds,
        }
        super().__init__(
            message=message,
            error_code="TOOL_ERROR",
            context=context
        )


class ValidationError(ImmoAssistError):
    """
    Raised when there are data validation errors.
    
    This includes input validation failures, schema validation errors,
    or business rule validation problems.
    """
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Optional[Any] = None
    ) -> None:
        context = {
            "field_name": field_name,
            "expected_type": expected_type,
            "actual_value": str(actual_value) if actual_value is not None else None,
        }
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            context=context
        )


class RagError(ImmoAssistError):
    """
    Raised when there are RAG (Retrieval Augmented Generation) errors.
    
    This includes vector database connection issues, search failures,
    or knowledge base access problems.
    """
    
    def __init__(
        self, 
        message: str, 
        corpus_name: Optional[str] = None,
        query: Optional[str] = None,
        error_type: Optional[str] = None
    ) -> None:
        context = {
            "corpus_name": corpus_name,
            "query": query,
            "error_type": error_type,
        }
        super().__init__(
            message=message,
            error_code="RAG_ERROR",
            context=context
        )


class IntegrationError(ImmoAssistError):
    """
    Raised when there are external service integration errors.
    
    This includes API call failures, authentication issues,
    or service unavailability problems.
    """
    
    def __init__(
        self, 
        message: str, 
        service_name: Optional[str] = None,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None
    ) -> None:
        context = {
            "service_name": service_name,
            "status_code": status_code,
            "request_id": request_id,
        }
        super().__init__(
            message=message,
            error_code="INTEGRATION_ERROR",
            context=context
        )


class RateLimitError(ImmoAssistError):
    """
    Raised when rate limits are exceeded.
    
    This includes API rate limits, request throttling,
    or quota exhaustion issues.
    """
    
    def __init__(
        self, 
        message: str, 
        limit_type: Optional[str] = None,
        retry_after_seconds: Optional[int] = None,
        current_usage: Optional[int] = None,
        limit_value: Optional[int] = None
    ) -> None:
        context = {
            "limit_type": limit_type,
            "retry_after_seconds": retry_after_seconds,
            "current_usage": current_usage,
            "limit_value": limit_value,
        }
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            context=context
        )


class SecurityError(ImmoAssistError):
    """
    Raised when there are security-related errors.
    
    This includes authentication failures, authorization issues,
    or security policy violations.
    """
    
    def __init__(
        self, 
        message: str, 
        security_context: Optional[str] = None,
        user_id: Optional[str] = None,
        action_attempted: Optional[str] = None
    ) -> None:
        context = {
            "security_context": security_context,
            "user_id": user_id,
            "action_attempted": action_attempted,
        }
        super().__init__(
            message=message,
            error_code="SECURITY_ERROR",
            context=context
        ) 