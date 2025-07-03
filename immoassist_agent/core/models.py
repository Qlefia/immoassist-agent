"""
Data models for ImmoAssist multi-agent system.

This module defines the core data models and structures used throughout
the system, providing type safety and clear data contracts.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class Language(str, Enum):
    """Supported languages."""
    GERMAN = "de"
    ENGLISH = "en"
    RUSSIAN = "ru"


class ExperienceLevel(str, Enum):
    """User experience levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PropertyType(str, Enum):
    """Property types."""
    APARTMENT = "apartment"
    HOUSE = "house"
    COMMERCIAL = "commercial"
    LAND = "land"


class CalculationType(str, Enum):
    """Calculation types."""
    CONSERVATIVE = "conservative"
    REALISTIC = "realistic"
    OPTIMISTIC = "optimistic"


@dataclass
class UserProfile:
    """User profile data structure."""
    
    language: Language = Language.GERMAN
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    investment_budget_min: Optional[float] = None
    investment_budget_max: Optional[float] = None
    preferred_locations: List[str] = field(default_factory=list)
    contact_method: str = "chat"
    timezone: str = "Europe/Berlin"
    currency_preference: str = "EUR"
    communication_style: str = "detailed"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class SessionState:
    """Session state data structure."""
    
    session_id: str
    user_profile: UserProfile = field(default_factory=UserProfile)
    session_start_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    topics_discussed: List[str] = field(default_factory=list)
    agents_consulted: List[str] = field(default_factory=list)
    session_version: str = "2.0"
    is_active: bool = True


@dataclass
class CalculationParameters:
    """Parameters for financial calculations."""
    
    purchase_price: float
    location: str
    property_type: PropertyType
    rental_income_monthly: Optional[float] = None
    down_payment_percentage: float = 20.0
    loan_interest_rate: float = 3.5
    loan_term_years: int = 30
    maintenance_cost_annual: Optional[float] = None
    property_tax_annual: Optional[float] = None
    calculation_type: CalculationType = CalculationType.REALISTIC


@dataclass
class CalculationResult:
    """Result of financial calculations."""
    
    calculation_id: str
    parameters: CalculationParameters
    roi_percentage: float
    cash_flow_monthly: float
    tax_benefits_annual: float
    break_even_years: float
    total_return_5_years: float
    risk_assessment: str
    scenarios: Dict[str, Dict[str, float]] = field(default_factory=dict)
    calculated_at: datetime = field(default_factory=datetime.now)


@dataclass
class PropertySearchCriteria:
    """Property search criteria."""
    
    location: str
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: PropertyType = PropertyType.APARTMENT
    min_size_sqm: Optional[float] = None
    max_size_sqm: Optional[float] = None
    energy_class: Optional[str] = None
    construction_year_min: Optional[int] = None
    search_radius_km: float = 10.0


@dataclass
class PropertyDetails:
    """Property details data structure."""
    
    property_id: str
    address: str
    city: str
    postal_code: str
    price: float
    size_sqm: float
    rooms: int
    property_type: PropertyType
    energy_class: str
    construction_year: int
    rental_yield_estimated: Optional[float] = None
    description: str = ""
    features: List[str] = field(default_factory=list)
    images: List[str] = field(default_factory=list)


@dataclass
class PropertySearchResult:
    """Result of property search."""
    
    search_id: str
    criteria: PropertySearchCriteria
    properties: List[PropertyDetails]
    total_found: int
    search_timestamp: datetime = field(default_factory=datetime.now)
    market_insights: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MarketAnalysisRequest:
    """Market analysis request parameters."""
    
    location: str
    analysis_type: str  # trends, forecast, comparison
    timeframe: str  # 1year, 2years, 5years
    property_types: List[PropertyType] = field(default_factory=list)
    include_demographics: bool = True
    include_infrastructure: bool = True


@dataclass
class MarketTrend:
    """Market trend data structure."""
    
    period: str
    average_price_change: float
    volume_change: float
    yield_change: float
    confidence_level: float


@dataclass
class MarketAnalysisResult:
    """Result of market analysis."""
    
    analysis_id: str
    request: MarketAnalysisRequest
    trends: List[MarketTrend]
    current_market_state: Dict[str, Any]
    future_outlook: Dict[str, Any]
    risk_factors: List[str]
    opportunities: List[str]
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class KnowledgeBaseEntry:
    """Knowledge base entry structure."""
    
    entry_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    entry_type: str  # faq, handbook, guide
    language: Language
    last_updated: datetime = field(default_factory=datetime.now)
    relevance_score: Optional[float] = None


@dataclass
class SearchResult:
    """Generic search result structure."""
    
    query: str
    results: List[KnowledgeBaseEntry]
    total_found: int
    search_timestamp: datetime = field(default_factory=datetime.now)
    search_duration_ms: Optional[int] = None


@dataclass
class AgentResponse:
    """Standardized agent response structure."""
    
    agent_name: str
    response_type: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_score: Optional[float] = None
    sources: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ToolExecutionResult:
    """Result of tool execution."""
    
    tool_name: str
    execution_id: str
    success: bool
    result: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SystemMetrics:
    """System performance and health metrics."""
    
    total_sessions: int = 0
    active_sessions: int = 0
    total_requests: int = 0
    average_response_time_ms: float = 0.0
    error_rate_percentage: float = 0.0
    agent_usage_stats: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now) 