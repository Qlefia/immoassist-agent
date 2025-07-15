"""
Configuration management for ImmoAssist.

Centralizes environment variables, feature flags, and system settings
for the ImmoAssist AI-powered real estate investment assistant.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Set default location to fix region mismatch issues
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west3")

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    
    host: str = "localhost"
    port: int = 5432
    database: str = "immoassist"
    username: str = "postgres"
    password: str = ""
    ssl_mode: str = "prefer"


@dataclass
class GoogleCloudConfig:
    """Google Cloud Platform configuration."""
    
    project_id: str = ""
    region: str = "europe-west3"
    service_account_file: Optional[str] = None
    vertex_ai_location: str = "europe-west3"


@dataclass
class ExternalServicesConfig:
    """External service integration configuration."""
    
    elevenlabs_api_key: Optional[str] = None
    heygen_api_key: Optional[str] = None
    email_service_endpoint: Optional[str] = None
    property_search_api_key: Optional[str] = None


@dataclass
class FeatureFlags:
    """Feature toggle configuration."""
    
    enable_voice_synthesis: bool = True
    enable_ai_avatar: bool = True
    enable_email_notifications: bool = True
    enable_conversation_history: bool = True
    enable_rag_knowledge_base: bool = True
    enable_property_search: bool = True
    enable_investment_calculations: bool = True


@dataclass
class SessionConfig:
    """Session management configuration."""
    
    session_timeout_minutes: int = 1440  # 24 hours
    max_concurrent_sessions: int = 1000
    conversation_history_limit: int = 50
    auto_cleanup_interval_hours: int = 6


class ImmoAssistConfig:
    """
    Central configuration manager for ImmoAssist application.
    
    Loads and validates environment variables, manages feature flags,
    and provides configuration access throughout the application.
    """
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        self._load_configuration()
        self._validate_required_settings()
        logger.info("ImmoAssist configuration loaded successfully")
    
    def _load_configuration(self) -> None:
        """Load configuration from environment variables."""
        
        # Database configuration
        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "immoassist"),
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            ssl_mode=os.getenv("DB_SSL_MODE", "prefer")
        )
        
        # Google Cloud configuration
        self.google_cloud = GoogleCloudConfig(
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            region=os.getenv("GOOGLE_CLOUD_REGION", "europe-west3"),
            service_account_file=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            vertex_ai_location=os.getenv("VERTEX_AI_LOCATION", "europe-west3")
        )
        
        # External services configuration
        self.external_services = ExternalServicesConfig(
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY"),
            heygen_api_key=os.getenv("HEYGEN_API_KEY"),
            email_service_endpoint=os.getenv("EMAIL_SERVICE_ENDPOINT"),
            property_search_api_key=os.getenv("PROPERTY_SEARCH_API_KEY")
        )
        
        # Feature flags (environment variables override defaults)
        self.features = FeatureFlags(
            enable_voice_synthesis=self._get_bool_env("ENABLE_VOICE_SYNTHESIS", True),
            enable_ai_avatar=self._get_bool_env("ENABLE_AI_AVATAR", True),
            enable_email_notifications=self._get_bool_env("ENABLE_EMAIL_NOTIFICATIONS", True),
            enable_conversation_history=self._get_bool_env("ENABLE_CONVERSATION_HISTORY", True),
            enable_rag_knowledge_base=self._get_bool_env("ENABLE_RAG_KNOWLEDGE_BASE", True),
            enable_property_search=self._get_bool_env("ENABLE_PROPERTY_SEARCH", True),
            enable_investment_calculations=self._get_bool_env("ENABLE_INVESTMENT_CALCULATIONS", True)
        )
        
        # Session configuration
        self.session = SessionConfig(
            session_timeout_minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "1440")),
            max_concurrent_sessions=int(os.getenv("MAX_CONCURRENT_SESSIONS", "1000")),
            conversation_history_limit=int(os.getenv("CONVERSATION_HISTORY_LIMIT", "50")),
            auto_cleanup_interval_hours=int(os.getenv("AUTO_CLEANUP_INTERVAL_HOURS", "6"))
        )
        
        # Application settings
        self.app_name = "ImmoAssist"
        self.app_version = os.getenv("APP_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug_mode = self._get_bool_env("DEBUG", False)
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
        # API settings
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8080"))
        self.api_workers = int(os.getenv("API_WORKERS", "4"))

        # Models - Restore for compatibility
        self.main_agent_model = os.getenv("MAIN_AGENT_MODEL", "gemini-2.5-flash")
        self.specialist_model = os.getenv("SPECIALIST_MODEL", "gemini-2.5-flash")
        self.chat_model = os.getenv("CHAT_MODEL", "gemini-2.5-flash")

        # RAG configuration
        self.rag_corpus = os.getenv("RAG_CORPUS")
    
    def _validate_required_settings(self) -> None:
        """Validate that required configuration is present."""
        required_settings = []
        
        # Check critical Google Cloud settings
        if not self.google_cloud.project_id:
            required_settings.append("GOOGLE_CLOUD_PROJECT")
        
        # Check for production environment requirements
        if self.environment == "production":
            if not self.external_services.elevenlabs_api_key and self.features.enable_voice_synthesis:
                logger.warning("ElevenLabs API key missing in production with voice synthesis enabled")
            
            if not self.external_services.heygen_api_key and self.features.enable_ai_avatar:
                logger.warning("HeyGen API key missing in production with AI avatar enabled")
        
        if required_settings:
            missing_vars = ", ".join(required_settings)
            raise ValueError(f"Required environment variables missing: {missing_vars}")
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def get_feature_flag(self, feature_name: str) -> bool:
        """
        Get feature flag status.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            True if feature is enabled, False otherwise
        """
        return getattr(self.features, feature_name, False)
    
    def get_database_url(self) -> str:
        """
        Get database connection URL.
        
        Returns:
            PostgreSQL connection URL
        """
        password_part = f":{self.database.password}" if self.database.password else ""
        return (
            f"postgresql://{self.database.username}{password_part}@"
            f"{self.database.host}:{self.database.port}/{self.database.database}"
            f"?sslmode={self.database.ssl_mode}"
        )
    
    def get_google_cloud_credentials(self) -> Optional[str]:
        """
        Get Google Cloud service account credentials path.
        
        Returns:
            Path to service account JSON file or None if not configured
        """
        return self.google_cloud.service_account_file

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.
        
        Returns:
            Dictionary with logging configuration
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                },
                "detailed": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "level": self.log_level,
                    "class": "logging.StreamHandler",
                    "formatter": "detailed" if self.debug_mode else "standard"
                }
            },
            "loggers": {
                "immoassist": {
                    "level": self.log_level,
                    "handlers": ["console"],
                    "propagate": False
                },
                "google.adk": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False
                }
            },
            "root": {
                "level": self.log_level,
                "handlers": ["console"]
            }
        }
    
    def export_config_summary(self) -> Dict[str, Any]:
        """
        Export configuration summary for debugging.
        
        Returns:
            Dictionary with non-sensitive configuration details
        """
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
            "google_cloud": {
                "project_id": self.google_cloud.project_id,
                "region": self.google_cloud.region,
                "vertex_ai_location": self.google_cloud.vertex_ai_location
            },
            "features": {
                "voice_synthesis": self.features.enable_voice_synthesis,
                "ai_avatar": self.features.enable_ai_avatar,
                "email_notifications": self.features.enable_email_notifications,
                "conversation_history": self.features.enable_conversation_history,
                "rag_knowledge_base": self.features.enable_rag_knowledge_base,
                "property_search": self.features.enable_property_search,
                "investment_calculations": self.features.enable_investment_calculations
            },
            "session": {
                "timeout_minutes": self.session.session_timeout_minutes,
                "max_concurrent": self.session.max_concurrent_sessions,
                "history_limit": self.session.conversation_history_limit
            },
            "api": {
                "host": self.api_host,
                "port": self.api_port,
                "workers": self.api_workers
            }
        }


# Global configuration instance
config = ImmoAssistConfig()
