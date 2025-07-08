"""
Enhanced exception handling for ImmoAssist enterprise system.

Following enterprise patterns with structured error reporting,
recovery strategies, and proper logging integration.
"""

from __future__ import annotations

import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, TypeVar

from .logging_config import log_error

# Type variables for generic error handling
F = TypeVar("F", bound=Callable[..., Any])


class ErrorSeverity(Enum):
    """Error severity levels for categorization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""

    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    INTERNAL = "internal"


class ImmoAssistException(Exception):
    """
    Base exception class for ImmoAssist with structured error information.

    Provides consistent error handling across the entire application
    with proper context, severity, and recovery information.
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory = ErrorCategory.INTERNAL,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: dict[str, Any] | None = None,
        recoverable: bool = True,
        retry_after_seconds: int | None = None,
        user_message: str | None = None,
        agent_name: str | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.recoverable = recoverable
        self.retry_after_seconds = retry_after_seconds
        self.user_message = user_message or "Ein unerwarteter Fehler ist aufgetreten."
        self.agent_name = agent_name
        self.timestamp = datetime.utcnow()
        self.stack_trace = traceback.format_exc()

        # Auto-log critical errors
        if severity == ErrorSeverity.CRITICAL:
            log_error(self, context=self.to_dict(), agent_name=agent_name)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "category": self.category.value,
            "severity": self.severity.value,
            "context": self.context,
            "recoverable": self.recoverable,
            "retry_after_seconds": self.retry_after_seconds,
            "user_message": self.user_message,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp.isoformat(),
            "stack_trace": (
                self.stack_trace if self.severity == ErrorSeverity.CRITICAL else None
            ),
        }


# === VALIDATION EXCEPTIONS ===


class ValidationError(ImmoAssistException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_name: str,
        invalid_value: Any = None,
        expected_format: str | None = None,
        **kwargs: Any,
    ) -> None:
        context = {
            "field_name": field_name,
            "invalid_value": str(invalid_value) if invalid_value is not None else None,
            "expected_format": expected_format,
        }
        context.update(kwargs.get("context", {}))

        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            context=context,
            recoverable=True,
            user_message=f"Ungültige Eingabe für {field_name}: {message}",
            **kwargs,
        )


class PropertyValidationError(ValidationError):
    """Specific validation error for property-related data."""

    def __init__(self, message: str, property_field: str, **kwargs: Any) -> None:
        super().__init__(
            message=message,
            field_name=property_field,
            user_message=f"Fehler bei Immobiliendaten: {message}",
            **kwargs,
        )


class FinancialValidationError(ValidationError):
    """Specific validation error for financial calculations."""

    def __init__(self, message: str, financial_field: str, **kwargs: Any) -> None:
        super().__init__(
            message=message,
            field_name=financial_field,
            user_message=f"Fehler bei Finanzberechnung: {message}",
            **kwargs,
        )


# === BUSINESS LOGIC EXCEPTIONS ===


class BusinessLogicError(ImmoAssistException):
    """Raised when business rules are violated."""

    def __init__(self, message: str, rule_name: str, **kwargs: Any) -> None:
        context = {"rule_name": rule_name}
        context.update(kwargs.get("context", {}))

        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            user_message=f"Geschäftsregel verletzt: {message}",
            **kwargs,
        )


class InvestmentCriteriaError(BusinessLogicError):
    """Raised when investment criteria are not met."""

    def __init__(self, message: str, criteria: list[str], **kwargs: Any) -> None:
        super().__init__(
            message=message,
            rule_name="investment_criteria",
            context={"failed_criteria": criteria},
            user_message=f"Investitionskriterien nicht erfüllt: {message}",
            **kwargs,
        )


# === EXTERNAL API EXCEPTIONS ===


class ExternalAPIError(ImmoAssistException):
    """Raised when external API calls fail."""

    def __init__(
        self,
        message: str,
        api_name: str,
        status_code: int | None = None,
        api_response: str | None = None,
        **kwargs: Any,
    ) -> None:
        context = {
            "api_name": api_name,
            "status_code": status_code,
            "api_response": api_response,
        }
        context.update(kwargs.get("context", {}))

        # Determine if retryable based on status code
        retryable = status_code is None or status_code >= 500 or status_code == 429
        retry_seconds = 30 if retryable else None

        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.HIGH
            if status_code and status_code >= 500
            else ErrorSeverity.MEDIUM,
            context=context,
            recoverable=retryable,
            retry_after_seconds=retry_seconds,
            user_message=f"Externe API {api_name} ist temporär nicht verfügbar.",
            **kwargs,
        )


class PropertyAPIError(ExternalAPIError):
    """Specific error for property search API failures."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message=message,
            api_name="property_search",
            user_message="Immobiliensuche temporär nicht verfügbar.",
            **kwargs,
        )


class HeyGenAPIError(ExternalAPIError):
    """Specific error for HeyGen avatar API failures."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message=message,
            api_name="heygen",
            user_message="AI-Avatar Service temporär nicht verfügbar.",
            **kwargs,
        )


class ElevenLabsAPIError(ExternalAPIError):
    """Specific error for ElevenLabs audio API failures."""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(
            message=message,
            api_name="elevenlabs",
            user_message="Sprachsynthese temporär nicht verfügbar.",
            **kwargs,
        )


# === AGENT-SPECIFIC EXCEPTIONS ===


class AgentError(ImmoAssistException):
    """Raised when agent execution fails."""

    def __init__(
        self, message: str, agent_name: str, operation: str, **kwargs: Any
    ) -> None:
        context = {"agent_name": agent_name, "operation": operation}
        context.update(kwargs.get("context", {}))

        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            context=context,
            agent_name=agent_name,
            user_message="Ein interner Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
            **kwargs,
        )


class AgentTimeoutError(AgentError):
    """Raised when agent operations timeout."""

    def __init__(
        self, agent_name: str, operation: str, timeout_seconds: int, **kwargs: Any
    ) -> None:
        super().__init__(
            message=f"Agent {agent_name} timed out during {operation} after {timeout_seconds}s",
            agent_name=agent_name,
            operation=operation,
            context={"timeout_seconds": timeout_seconds},
            user_message="Die Anfrage dauert länger als erwartet. Bitte versuchen Sie es erneut.",
            **kwargs,
        )


class AgentCommunicationError(AgentError):
    """Raised when agents fail to communicate."""

    def __init__(self, source_agent: str, target_agent: str, **kwargs: Any) -> None:
        super().__init__(
            message=f"Communication failed between {source_agent} and {target_agent}",
            agent_name=source_agent,
            operation="agent_communication",
            context={"target_agent": target_agent},
            user_message="Interner Kommunikationsfehler. Bitte versuchen Sie es erneut.",
            **kwargs,
        )


# === CONFIGURATION EXCEPTIONS ===


class ConfigurationError(ImmoAssistException):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str, **kwargs: Any) -> None:
        context = {"config_key": config_key}
        context.update(kwargs.get("context", {}))

        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            context=context,
            recoverable=False,
            user_message="Systemkonfigurationsfehler. Bitte kontaktieren Sie den Support.",
            **kwargs,
        )


# === EXCEPTION HANDLING UTILITIES ===


def handle_exception(
    func_name: str,
    exception: Exception,
    agent_name: str | None = None,
    context: dict[str, Any] | None = None,
) -> ImmoAssistException:
    """
    Convert any exception to a structured ImmoAssistException.

    Args:
        func_name: Name of the function where exception occurred
        exception: The original exception
        agent_name: Name of the agent where exception occurred
        context: Additional context information

    Returns:
        Structured ImmoAssistException
    """
    if isinstance(exception, ImmoAssistException):
        return exception

    # Map common exception types
    if isinstance(exception, ValueError):
        return ValidationError(
            message=str(exception),
            field_name="unknown",
            agent_name=agent_name,
            context={
                "original_exception": type(exception).__name__,
                "function": func_name,
                **(context or {}),
            },
        )

    if isinstance(exception, TimeoutError):
        return AgentTimeoutError(
            agent_name=agent_name or "unknown",
            operation=func_name,
            timeout_seconds=30,
            context=context,
        )

    if isinstance(exception, ConnectionError):
        return ExternalAPIError(
            message=str(exception),
            api_name="unknown",
            agent_name=agent_name,
            context={
                "original_exception": type(exception).__name__,
                "function": func_name,
                **(context or {}),
            },
        )

    # Default to generic agent error
    return AgentError(
        message=str(exception),
        agent_name=agent_name or "unknown",
        operation=func_name,
        context={"original_exception": type(exception).__name__, **(context or {})},
    )


def safe_execute(
    func: Callable[..., Any],
    agent_name: str | None = None,
    operation: str = "unknown",
    context: dict[str, Any] | None = None,
) -> Callable[..., Any]:
    """
    Decorator to safely execute functions with proper exception handling.

    Args:
        func: Function to execute safely
        agent_name: Name of the agent executing the function
        operation: Description of the operation being performed
        context: Additional context information

    Returns:
        Wrapped function with exception handling
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            structured_exception = handle_exception(
                func_name=operation, exception=e, agent_name=agent_name, context=context
            )
            log_error(
                structured_exception,
                context=structured_exception.to_dict(),
                agent_name=agent_name,
            )
            raise structured_exception from e

    return wrapper
