"""
Centralized configuration management for ImmoAssist multi-agent system.

This module provides a single source of truth for all configuration values,
following the principle of dependency inversion and making the system
easily configurable for different environments.
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv
import logging

load_dotenv()


@dataclass(frozen=True)
class ModelConfig:
    """Configuration for AI models and Vertex AI settings."""
    
    name: str = "gemini-2.5-pro"
    location: str = "europe-west1"
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    top_k: int = 40


@dataclass(frozen=True)
class SessionConfig:
    """Configuration for session management."""
    
    timeout_minutes: int = 60
    max_conversation_history: int = 100
    default_language: str = "de"
    supported_languages: List[str] = field(default_factory=lambda: ["de", "en", "ru"])
    analytics_enabled: bool = True
    session_encryption_enabled: bool = True


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for individual agents."""
    
    knowledge_agent_name: str = "knowledge_specialist"
    property_agent_name: str = "property_specialist"
    calculator_agent_name: str = "calculator_specialist"
    analytics_agent_name: str = "analytics_specialist"
    root_agent_name: str = "Philipp_ImmoAssist_Coordinator"
    
    # Tool configuration
    rag_similarity_threshold: float = 0.6
    rag_top_k: int = 5
    search_timeout_seconds: int = 30


@dataclass(frozen=True)
class LoggingConfig:
    """Configuration for logging and monitoring."""
    
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "immoassist_agent.log"
    structured_logging: bool = True
    correlation_id_enabled: bool = True


@dataclass(frozen=True)
class SecurityConfig:
    """Configuration for security settings."""
    
    enable_vpc_sc: bool = True
    require_authentication: bool = True
    max_session_duration_hours: int = 8
    data_encryption_at_rest: bool = True
    audit_logging_enabled: bool = True
    rate_limiting_enabled: bool = True
    max_requests_per_minute: int = 100


@dataclass(frozen=True)
class IntegrationConfig:
    """Configuration for external service integrations."""
    
    heygen_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    calendly_api_key: Optional[str] = None
    email_service_enabled: bool = False
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    
    def __post_init__(self) -> None:
        """Load API keys from environment after initialization."""
        object.__setattr__(self, 'heygen_api_key', os.getenv('HEYGEN_API_KEY'))
        object.__setattr__(self, 'elevenlabs_api_key', os.getenv('ELEVENLABS_API_KEY'))
        object.__setattr__(self, 'calendly_api_key', os.getenv('CALENDLY_API_KEY'))


class ImmoAssistConfig:
    """
    Central configuration manager for ImmoAssist multi-agent system.
    
    This class provides a single point of configuration management,
    following the dependency inversion principle and enabling easy
    environment-specific configuration.
    
    Features:
        - Environment-based configuration loading
        - Validation of required settings
        - Type-safe configuration access
        - Hot reload capability for development
        - Configuration export for deployment
    """
    
    def __init__(self, environment: str = "production") -> None:
        """
        Initialize configuration manager.
        
        Args:
            environment: Target environment (development, staging, production)
            
        Raises:
            ConfigurationError: If required configuration is missing
        """
        self.environment = environment
        self._logger = logging.getLogger(__name__)
        
        # Load and validate configuration
        self.model = ModelConfig()
        self.session = SessionConfig()
        self.agents = AgentConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        self.integration = IntegrationConfig()
        
        # Google Cloud configuration
        self.google_cloud_project: Optional[str] = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.rag_corpus: Optional[str] = os.getenv("RAG_CORPUS")
        
        # Validate critical configuration
        self._validate_configuration()
        
        self._logger.info(f"Configuration loaded for environment: {environment}")
    
    def _validate_configuration(self) -> None:
        """
        Validate that all required configuration is present.
        
        Raises:
            ConfigurationError: If validation fails
        """
        from .exceptions import ConfigurationError
        
        errors = []
        
        # Validate environment-specific requirements
        if self.environment == "production":
            if not self.security.require_authentication:
                errors.append("Authentication must be enabled in production")
            
            if not self.security.audit_logging_enabled:
                errors.append("Audit logging must be enabled in production")
        
        # Validate Google Cloud configuration
        if not self.google_cloud_project and self.environment != "development":
            self._logger.warning("Google Cloud project not configured - using ADC auto-detection")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Dictionary containing agent-specific configuration
        """
        base_config = {
            "model_name": self.model.name,
            "location": self.model.location,
            "temperature": self.model.temperature,
            "max_tokens": self.model.max_tokens,
            "timeout_seconds": self.agents.search_timeout_seconds,
        }
        
        # Add agent-specific configuration
        if agent_name == self.agents.knowledge_agent_name:
            base_config.update({
                "rag_corpus": self.rag_corpus,
                "similarity_threshold": self.agents.rag_similarity_threshold,
                "top_k": self.agents.rag_top_k,
            })
        
        return base_config
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Export configuration as dictionary for serialization.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "environment": self.environment,
            "model": self.model.__dict__,
            "session": self.session.__dict__,
            "agents": self.agents.__dict__,
            "logging": self.logging.__dict__,
            "security": {k: v for k, v in self.security.__dict__.items() if not k.endswith('_key')},
            "google_cloud_project": self.google_cloud_project,
            "rag_corpus_configured": bool(self.rag_corpus),
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "ImmoAssistConfig":
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            ImmoAssistConfig instance
        """
        config = cls(environment=config_dict.get("environment", "production"))
        
        # Override with provided values
        for section_name, section_data in config_dict.items():
            if hasattr(config, section_name) and isinstance(section_data, dict):
                section = getattr(config, section_name)
                for key, value in section_data.items():
                    if hasattr(section, key):
                        setattr(section, key, value)
        
        return config
    
    def reload(self) -> None:
        """Reload configuration from environment variables."""
        load_dotenv(override=True)
        self.__init__(self.environment)
        self._logger.info("Configuration reloaded from environment")


# Global configuration instance
config = ImmoAssistConfig() 