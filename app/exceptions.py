"""
Enhanced exception handling for ImmoAssist enterprise system.

Following enterprise patterns with structured error reporting,
recovery strategies, and proper logging integration.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import traceback

from .logging_config import log_error


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
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
        retry_after_seconds: Optional[int] = None,
        user_message: Optional[str] = None,
        agent_name: Optional[str] = None
    ):
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
    
    def to_dict(self) -> Dict[str, Any]:
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
            "stack_trace": self.stack_trace if self.severity == ErrorSeverity.CRITICAL else None
        }


# === VALIDATION EXCEPTIONS ===

class ValidationError(ImmoAssistException):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field_name: str,
        invalid_value: Any = None,
        expected_format: Optional[str] = None,
        **kwargs
    ):
        context = {
            "field_name": field_name,
            "invalid_value": str(invalid_value) if invalid_value is not None else None,
            "expected_format": expected_format
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
            **kwargs
        )


class PropertyValidationError(ValidationError):
    """Specific validation error for property-related data."""
    
    def __init__(self, message: str, property_field: str, **kwargs):
        super().__init__(
            message=message,
            field_name=property_field,
            user_message=f"Fehler bei Immobiliendaten: {message}",
            **kwargs
        )


class FinancialValidationError(ValidationError):
    """Specific validation error for financial calculations."""
    
    def __init__(self, message: str, financial_field: str, **kwargs):
        super().__init__(
            message=message,
            field_name=financial_field,
            user_message=f"Fehler bei Finanzberechnung: {message}",
            **kwargs
        )


# === BUSINESS LOGIC EXCEPTIONS ===

class BusinessLogicError(ImmoAssistException):
    """Raised when business rules are violated."""
    
    def __init__(self, message: str, rule_name: str, **kwargs):
        context = {"rule_name": rule_name}
        context.update(kwargs.get("context", {}))
        
        super().__init__(
            message=message,
            error_code="BUSINESS_RULE_VIOLATION",
            category=ErrorCategory.BUSINESS_LOGIC,
            severity=ErrorSeverity.MEDIUM,
            context=context,
            user_message=f"Geschäftsregel verletzt: {message}",
            **kwargs
        )


class InvestmentCriteriaError(BusinessLogicError):
    """Raised when investment criteria are not met."""
    
    def __init__(self, message: str, criteria: List[str], **kwargs):
        super().__init__(
            message=message,
            rule_name="investment_criteria",
            context={"failed_criteria": criteria},
            user_message=f"Investitionskriterien nicht erfüllt: {message}",
            **kwargs
        )


# === EXTERNAL API EXCEPTIONS ===

class ExternalAPIError(ImmoAssistException):
    """Raised when external API calls fail."""
    
    def __init__(
        self,
        message: str,
        api_name: str,
        status_code: Optional[int] = None,
        api_response: Optional[str] = None,
        **kwargs
    ):
        context = {
            "api_name": api_name,
            "status_code": status_code,
            "api_response": api_response
        }
        context.update(kwargs.get("context", {}))
        
        # Determine if retryable based on status code
        recoverable = status_code is None or status_code >= 500 or status_code == 429
        retry_after = 30 if recoverable else None
        
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            category=ErrorCategory.EXTERNAL_API,
            severity=ErrorSeverity.HIGH if not recoverable else ErrorSeverity.MEDIUM,
            context=context,
            recoverable=recoverable,
            retry_after_seconds=retry_after,
            user_message="Externe Dienste sind temporär nicht verfügbar. Bitte versuchen Sie es später erneut.",
            **kwargs
        )


class PropertyAPIError(ExternalAPIError):
    """Specific error for property data API failures."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            api_name="property_api",
            user_message="Immobiliendaten konnten nicht abgerufen werden. Bitte versuchen Sie es später erneut.",
            **kwargs
        )


class HeyGenAPIError(ExternalAPIError):
    """Specific error for HeyGen API failures."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            api_name="heygen",
            user_message="Avatar-Erstellung temporär nicht verfügbar.",
            **kwargs
        )


class ElevenLabsAPIError(ExternalAPIError):
    """Specific error for ElevenLabs API failures."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            api_name="elevenlabs",
            user_message="Sprachsynthese temporär nicht verfügbar.",
            **kwargs
        )


# === AGENT EXCEPTIONS ===

class AgentError(ImmoAssistException):
    """Raised when agent processing fails."""
    
    def __init__(
        self,
        message: str,
        agent_name: str,
        operation: str,
        **kwargs
    ):
        context = {"operation": operation}
        context.update(kwargs.get("context", {}))
        
        super().__init__(
            message=message,
            error_code="AGENT_ERROR",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            context=context,
            agent_name=agent_name,
            user_message="Die Anfrage konnte nicht verarbeitet werden. Bitte versuchen Sie es erneut.",
            **kwargs
        )


class AgentTimeoutError(AgentError):
    """Raised when agent operations timeout."""
    
    def __init__(self, agent_name: str, operation: str, timeout_seconds: int, **kwargs):
        super().__init__(
            message=f"Agent {agent_name} timed out during {operation} after {timeout_seconds}s",
            agent_name=agent_name,
            operation=operation,
            context={"timeout_seconds": timeout_seconds},
            recoverable=True,
            retry_after_seconds=5,
            user_message="Die Anfrage dauert länger als erwartet. Bitte versuchen Sie es erneut.",
            **kwargs
        )


class AgentCommunicationError(AgentError):
    """Raised when agents fail to communicate properly."""
    
    def __init__(self, source_agent: str, target_agent: str, **kwargs):
        super().__init__(
            message=f"Communication failed between {source_agent} and {target_agent}",
            agent_name=source_agent,
            operation="agent_communication",
            context={"target_agent": target_agent},
            user_message="Interne Kommunikation fehlgeschlagen. Bitte versuchen Sie es erneut.",
            **kwargs
        )


# === CONFIGURATION EXCEPTIONS ===

class ConfigurationError(ImmoAssistException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key: str, **kwargs):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.CRITICAL,
            context={"config_key": config_key},
            recoverable=False,
            user_message="Systemkonfigurationsfehler. Bitte kontaktieren Sie den Support.",
            **kwargs
        )


# === ERROR HANDLING UTILITIES ===

def handle_exception(
    func_name: str,
    exception: Exception,
    agent_name: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ImmoAssistException:
    """
    Convert generic exceptions to structured ImmoAssist exceptions.
    
    Args:
        func_name: Name of function where error occurred
        exception: Original exception
        agent_name: Name of agent if applicable
        context: Additional context
        
    Returns:
        Structured ImmoAssist exception
    """
    
    # If already an ImmoAssist exception, return as-is
    if isinstance(exception, ImmoAssistException):
        return exception
    
    # Map common exception types
    if isinstance(exception, ValueError):
        return ValidationError(
            message=str(exception),
            field_name="unknown",
            context=context,
            agent_name=agent_name
        )
    elif isinstance(exception, (ConnectionError, TimeoutError)):
        return ExternalAPIError(
            message=str(exception),
            api_name="unknown",
            context=context,
            agent_name=agent_name
        )
    else:
        # Generic internal error
        return ImmoAssistException(
            message=f"Unexpected error in {func_name}: {str(exception)}",
            error_code="INTERNAL_ERROR",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            context=context,
            agent_name=agent_name,
            recoverable=True
        )


def safe_execute(
    func,
    agent_name: Optional[str] = None,
    operation: str = "unknown",
    context: Optional[Dict[str, Any]] = None
):
    """
    Safely execute a function with proper error handling.
    
    Args:
        func: Function to execute
        agent_name: Name of agent executing
        operation: Description of operation
        context: Additional context
        
    Returns:
        Function result or raises ImmoAssistException
    """
    try:
        return func()
    except ImmoAssistException:
        raise
    except Exception as e:
        structured_error = handle_exception(
            func_name=operation,
            exception=e,
            agent_name=agent_name,
            context=context
        )
        log_error(structured_error, context=context, agent_name=agent_name)
        raise structured_error 