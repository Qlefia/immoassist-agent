"""
Enterprise logging system for ImmoAssist multi-agent system.

This module provides structured logging with correlation IDs, performance metrics,
and comprehensive error tracking for production deployment and debugging.
"""

import logging
import json
import uuid
import time
from typing import Dict, Any, Optional
from datetime import datetime
from contextvars import ContextVar
from functools import wraps

from .config import ImmoAssistConfig
from .exceptions import ImmoAssistError


# Context variable for correlation ID tracking
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logging.
    
    Provides consistent log format with correlation IDs, timestamps,
    and contextual information for enterprise monitoring systems.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as structured JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id.get(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields from log call
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ImmoAssistLogger:
    """
    Enhanced logger for ImmoAssist with correlation tracking and performance metrics.
    
    Features:
        - Automatic correlation ID injection
        - Performance timing decorators
        - Structured error logging
        - Agent operation tracking
        - Session lifecycle logging
    """
    
    def __init__(self, name: str, config: Optional[ImmoAssistConfig] = None) -> None:
        """
        Initialize enhanced logger.
        
        Args:
            name: Logger name (typically module name)
            config: Configuration object for logging settings
        """
        self.name = name
        self.config = config or ImmoAssistConfig()
        self._logger = logging.getLogger(name)
        
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Configure logger with appropriate handlers and formatters."""
        self._logger.setLevel(getattr(logging, self.config.logging.level))
        
        # Clear existing handlers to avoid duplicates
        self._logger.handlers.clear()
        
        # Console handler with structured formatting
        console_handler = logging.StreamHandler()
        if self.config.logging.structured_logging:
            console_handler.setFormatter(StructuredFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter(self.config.logging.format)
            )
        self._logger.addHandler(console_handler)
        
        # File handler if enabled
        if self.config.logging.file_enabled:
            file_handler = logging.FileHandler(self.config.logging.file_path)
            file_handler.setFormatter(StructuredFormatter())
            self._logger.addHandler(file_handler)
    
    def _log_with_context(
        self, 
        level: int, 
        message: str, 
        extra_fields: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None
    ) -> None:
        """
        Log message with enhanced context information.
        
        Args:
            level: Logging level
            message: Log message
            extra_fields: Additional fields to include
            correlation_id_override: Override correlation ID for this log
        """
        # Set correlation ID if provided
        if correlation_id_override:
            token = correlation_id.set(correlation_id_override)
        
        # Create log record with extra fields
        extra = {"extra_fields": extra_fields or {}}
        self._logger.log(level, message, extra=extra)
        
        # Reset correlation ID if it was overridden
        if correlation_id_override:
            correlation_id.reset(token)
    
    def info(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None
    ) -> None:
        """Log info level message."""
        self._log_with_context(logging.INFO, message, extra, correlation_id_override)
    
    def warning(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None
    ) -> None:
        """Log warning level message."""
        self._log_with_context(logging.WARNING, message, extra, correlation_id_override)
    
    def error(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None,
        exc_info: bool = True
    ) -> None:
        """Log error level message with exception info."""
        self._log_with_context(logging.ERROR, message, extra, correlation_id_override)
        if exc_info:
            self._logger.error(message, exc_info=True, extra={"extra_fields": extra or {}})
    
    def debug(
        self, 
        message: str, 
        extra: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None
    ) -> None:
        """Log debug level message."""
        self._log_with_context(logging.DEBUG, message, extra, correlation_id_override)
    
    def log_exception(
        self, 
        exception: Exception, 
        context: Optional[Dict[str, Any]] = None,
        correlation_id_override: Optional[str] = None
    ) -> None:
        """
        Log exception with enhanced context.
        
        Args:
            exception: Exception to log
            context: Additional context information
            correlation_id_override: Override correlation ID
        """
        extra_fields = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
        }
        
        # Add ImmoAssist exception context if available
        if isinstance(exception, ImmoAssistError):
            extra_fields.update({
                "error_code": exception.error_code,
                "error_context": exception.context,
                "error_cause": str(exception.cause) if exception.cause else None,
            })
        
        # Add additional context
        if context:
            extra_fields["context"] = context
        
        self.error(
            f"Exception occurred: {str(exception)}",
            extra=extra_fields,
            correlation_id_override=correlation_id_override
        )
    
    def log_agent_operation(
        self, 
        agent_name: str, 
        operation: str, 
        status: str,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log agent operation with performance metrics.
        
        Args:
            agent_name: Name of the agent
            operation: Operation being performed
            status: Operation status (started, completed, failed)
            duration_ms: Operation duration in milliseconds
            metadata: Additional operation metadata
        """
        extra_fields = {
            "agent_name": agent_name,
            "operation": operation,
            "status": status,
            "operation_type": "agent_operation",
        }
        
        if duration_ms is not None:
            extra_fields["duration_ms"] = duration_ms
        
        if metadata:
            extra_fields["metadata"] = metadata
        
        message = f"Agent operation - {agent_name}: {operation} ({status})"
        if duration_ms:
            message += f" - {duration_ms}ms"
        
        self.info(message, extra=extra_fields)
    
    def log_session_event(
        self, 
        session_id: str, 
        event_type: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log session lifecycle events.
        
        Args:
            session_id: Session identifier
            event_type: Type of session event
            user_id: User identifier if available
            metadata: Additional event metadata
        """
        extra_fields = {
            "session_id": session_id,
            "event_type": event_type,
            "operation_type": "session_event",
        }
        
        if user_id:
            extra_fields["user_id"] = user_id
        
        if metadata:
            extra_fields["metadata"] = metadata
        
        self.info(
            f"Session event - {session_id}: {event_type}",
            extra=extra_fields
        )


def correlation_context(correlation_id_value: Optional[str] = None):
    """
    Decorator to set correlation ID context for function execution.
    
    Args:
        correlation_id_value: Correlation ID to use (generates new if None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate correlation ID if not provided
            corr_id = correlation_id_value or str(uuid.uuid4())
            
            # Set correlation ID context
            token = correlation_id.set(corr_id)
            
            try:
                return func(*args, **kwargs)
            finally:
                # Reset correlation ID context
                correlation_id.reset(token)
        
        return wrapper
    return decorator


def time_operation(logger: ImmoAssistLogger, operation_name: str):
    """
    Decorator to time function execution and log performance metrics.
    
    Args:
        logger: Logger instance to use
        operation_name: Name of the operation being timed
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                logger.info(
                    f"Starting operation: {operation_name}",
                    extra={"operation_name": operation_name, "status": "started"}
                )
                
                result = func(*args, **kwargs)
                
                duration_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    f"Completed operation: {operation_name} ({duration_ms}ms)",
                    extra={
                        "operation_name": operation_name,
                        "status": "completed",
                        "duration_ms": duration_ms
                    }
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                logger.log_exception(
                    e,
                    context={
                        "operation_name": operation_name,
                        "status": "failed",
                        "duration_ms": duration_ms
                    }
                )
                raise
        
        return wrapper
    return decorator


# Global logger factory
def get_logger(name: str, config: Optional[ImmoAssistConfig] = None) -> ImmoAssistLogger:
    """
    Get logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
        config: Configuration object
        
    Returns:
        ImmoAssistLogger instance
    """
    return ImmoAssistLogger(name, config) 