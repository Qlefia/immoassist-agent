"""
Structured logging configuration for ImmoAssist.

Following gemini-fullstack best practices for enterprise-level logging,
monitoring, and observability.
"""

import logging
import logging.config
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from .config import config


class StructuredFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Provides consistent, machine-readable log format.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        
        # Base log structure
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add thread and process info
        if record.thread:
            log_entry["thread_id"] = record.thread
        if record.process:
            log_entry["process_id"] = record.process
            
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
            
        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                          'pathname', 'filename', 'module', 'lineno', 
                          'funcName', 'created', 'msecs', 'relativeCreated',
                          'thread', 'threadName', 'processName', 'process',
                          'message', 'exc_info', 'exc_text', 'stack_info']:
                log_entry[key] = value
                
        return json.dumps(log_entry, ensure_ascii=False)


class AgentContextFilter(logging.Filter):
    """
    Filter to add agent context to log records.
    Helps trace agent interactions across the system.
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add agent context to log record."""
        
        # Add default agent context if not present
        if not hasattr(record, 'agent'):
            record.agent = "unknown"
        if not hasattr(record, 'session_id'):
            record.session_id = "no_session"
        if not hasattr(record, 'user_id'):
            record.user_id = "anonymous"
            
        return True


def setup_logging() -> None:
    """
    Configure structured logging for the application.
    
    Sets up different handlers for different environments:
    - Development: Console with readable format
    - Production: Structured JSON for log aggregation
    """
    
    # Determine log level
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Base logging configuration
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter
            },
            "simple": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "filters": {
            "agent_context": {
                "()": AgentContextFilter
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "simple" if config.is_development() else "structured",
                "stream": sys.stdout,
                "filters": ["agent_context"]
            },
            "file_structured": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level,
                "formatter": "structured",
                "filename": log_dir / "immoassist.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "filters": ["agent_context"]
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler", 
                "level": "ERROR",
                "formatter": "structured",
                "filename": log_dir / "errors.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "filters": ["agent_context"]
            }
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": ["console", "file_structured"],
                "propagate": False
            },
            "app.agent": {
                "level": log_level,
                "handlers": ["console", "file_structured"],
                "propagate": False
            },
            "app.tools": {
                "level": log_level,
                "handlers": ["console", "file_structured"],
                "propagate": False
            },
            "app.services": {
                "level": log_level,
                "handlers": ["console", "file_structured"],
                "propagate": False
            }
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "error_file"]
        }
    }
    
    # Apply configuration
    logging.config.dictConfig(logging_config)
    
    # Create module-specific loggers
    app_logger = logging.getLogger("app")
    app_logger.info("Structured logging initialized", 
                   extra={"environment": config.environment,
                          "log_level": config.log_level,
                          "structured_logging": config.enable_structured_logging})


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger for a module.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{name}")


def log_agent_performance(
    agent_name: str, 
    operation: str, 
    duration_ms: float,
    success: bool = True,
    **kwargs
) -> None:
    """
    Log agent performance metrics.
    
    Args:
        agent_name: Name of the agent
        operation: Operation performed
        duration_ms: Duration in milliseconds
        success: Whether operation succeeded
        **kwargs: Additional context
    """
    logger = get_logger("performance")
    
    log_data = {
        "agent": agent_name,
        "operation": operation,
        "duration_ms": duration_ms,
        "success": success,
        **kwargs
    }
    
    if success:
        logger.info(f"Agent {agent_name} completed {operation}", extra=log_data)
    else:
        logger.warning(f"Agent {agent_name} failed {operation}", extra=log_data)


def log_user_interaction(
    user_id: str,
    session_id: str,
    interaction_type: str,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user interaction for analytics.
    
    Args:
        user_id: User identifier
        session_id: Session identifier  
        interaction_type: Type of interaction
        details: Additional interaction details
    """
    logger = get_logger("user_interactions")
    
    log_data = {
        "user_id": user_id,
        "session_id": session_id,
        "interaction_type": interaction_type,
        "details": details or {}
    }
    
    logger.info(f"User interaction: {interaction_type}", extra=log_data)


def log_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    agent_name: Optional[str] = None
) -> None:
    """
    Log structured error information.
    
    Args:
        error: Exception that occurred
        context: Additional error context
        agent_name: Name of agent where error occurred
    """
    logger = get_logger("errors")
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
    }
    
    if agent_name:
        log_data["agent"] = agent_name
        
    logger.error(f"Error in {agent_name or 'system'}: {str(error)}", 
                extra=log_data, exc_info=True)


# Initialize logging when module is imported
if config.enable_structured_logging:
    setup_logging() 