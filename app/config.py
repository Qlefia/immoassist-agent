# Copyright 2025 ImmoAssist
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import google.auth

# Setup Google Cloud environment
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1") 
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ImmoAssistConfiguration:
    """
    Enterprise configuration for ImmoAssist real estate agent system.
    
    Follows SOLID principles with clean separation of concerns and
    supports multiple deployment environments (dev, staging, production).
    """
    
    # === CORE MODELS ===
    main_agent_model: str = "gemini-2.5-flash"
    specialist_model: str = "gemini-2.5-flash"
    critic_model: str = "gemini-2.5-pro"  # For evaluation tasks
    
    # === ENVIRONMENT ===
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # === GOOGLE CLOUD ===
    project_id: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT"))
    location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1"))
    
    # === RAG & KNOWLEDGE BASE ===
    rag_corpus: Optional[str] = field(default_factory=lambda: os.getenv("RAG_CORPUS"))
    knowledge_base_path: str = field(default_factory=lambda: os.getenv("KNOWLEDGE_BASE_PATH", "./data"))
    
    # === REAL ESTATE DOMAIN ===
    property_price_range: Dict[str, int] = field(default_factory=lambda: {
        "min": 250000,
        "max": 500000
    })
    supported_languages: List[str] = field(default_factory=lambda: ["de", "en", "ru"])
    default_language: str = "de"
    target_energy_classes: List[str] = field(default_factory=lambda: ["A+", "A", "B+"])
    
    # === AGENT BEHAVIOR ===
    max_retries: int = 3
    agent_timeout_seconds: int = 30
    enable_thinking: bool = True
    enable_memory: bool = True
    
    # === SESSION MANAGEMENT ===
    session_timeout_minutes: int = 60
    max_concurrent_sessions: int = 1000
    enable_conversation_history: bool = True
    
    # === INTEGRATION SETTINGS ===
    # External API configurations
    heygen_api_key: Optional[str] = field(default_factory=lambda: os.getenv("HEYGEN_API_KEY"))
    elevenlabs_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY"))
    
    # Database integrations
    database_url: Optional[str] = field(default_factory=lambda: os.getenv("DATABASE_URL"))
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    
    # Website backend integration
    website_api_base_url: Optional[str] = field(default_factory=lambda: os.getenv("WEBSITE_API_BASE_URL"))
    website_api_key: Optional[str] = field(default_factory=lambda: os.getenv("WEBSITE_API_KEY"))
    
    # === BUSINESS LOGIC ===
    # Financial calculation defaults
    default_loan_interest_rate: float = 3.5
    default_loan_term_years: int = 30
    default_tax_rate: float = 0.42
    special_depreciation_rate: float = 0.05  # 5% for new buildings
    
    # Property search defaults
    default_search_radius_km: int = 50
    max_search_results: int = 50
    enable_property_cache: bool = True
    cache_ttl_hours: int = 24
    
    # === FEATURE FLAGS ===
    feature_flags: Dict[str, bool] = field(default_factory=lambda: {
        "enable_3d_visualization": True,
        "enable_ai_avatar": True,
        "enable_voice_synthesis": True,
        "enable_advanced_analytics": True,
        "enable_market_predictions": False,  # Beta feature
        "enable_automated_valuations": True,
        "enable_document_analysis": True
    })
    
    # === LOGGING & MONITORING ===
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    enable_structured_logging: bool = True
    enable_performance_monitoring: bool = True
    enable_error_tracking: bool = True
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def get_feature_flag(self, flag_name: str, default: bool = False) -> bool:
        """Get feature flag value with fallback."""
        return self.feature_flags.get(flag_name, default)
    
    def validate_environment(self) -> None:
        """Validate environment-specific requirements."""
        if self.is_production():
            # Production validation
            if not self.project_id:
                raise ValueError("GOOGLE_CLOUD_PROJECT must be set in production")
            
            if self.debug:
                raise ValueError("Debug mode should not be enabled in production")
                
        # Validate API keys for enabled features
        if self.get_feature_flag("enable_ai_avatar") and not self.heygen_api_key:
            import warnings
            warnings.warn("HeyGen API key not configured but AI avatar feature is enabled")
            
        if self.get_feature_flag("enable_voice_synthesis") and not self.elevenlabs_api_key:
            import warnings
            warnings.warn("ElevenLabs API key not configured but voice synthesis is enabled")


# === GLOBAL CONFIG INSTANCE ===
config = ImmoAssistConfiguration()

# Validate on import
config.validate_environment() 