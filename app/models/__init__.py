"""
Domain models for ImmoAssist enterprise system.

This module exports all domain models used across the application,
following clean architecture principles with clear separation of concerns.
"""

from .financial import (
    FinancialCalculation,
    InvestmentMetrics,
    LoanDetails,
    ROICalculation,
    TaxBenefits,
)

# Structured output schemas for tools and agents
from .output_schemas import (
    # Error handling
    AgentError,
    # Financial calculation outputs
    CalculationSummary,
    ElevenLabsResponse,
    GermanTaxBenefits,
    # Integration outputs
    HeyGenResponse,
    InvestmentCalculationResult,
    InvestmentRecommendation,
    # Knowledge base outputs
    KnowledgeSearchResult,
    ProcessGuide,
    ProcessGuideStep,
    PropertyDetailFinancials,
    PropertyDetailLocation,
    PropertyDetails,
    PropertyDetailSpecs,
    # Property outputs
    PropertySearchItem,
)
from .output_schemas import PropertySearchResult as PropertySearchOutputResult
from .property import (
    Property,
    PropertyLocation,
    PropertySearchCriteria,
    PropertySearchResult,
)
from .user import (
    ConversationHistory,
    UserInteraction,
    UserPreferences,
    UserProfile,
    UserSession,
)

__all__ = [
    "AgentError",
    "CalculationSummary",
    "ConversationHistory",
    "ElevenLabsResponse",
    "FinancialCalculation",
    "GermanTaxBenefits",
    "HeyGenResponse",
    "InvestmentCalculationResult",
    "InvestmentMetrics",
    "InvestmentRecommendation",
    "KnowledgeSearchResult",
    "LoanDetails",
    "ProcessGuide",
    "ProcessGuideStep",
    # Domain models
    "Property",
    "PropertyDetailFinancials",
    "PropertyDetailLocation",
    "PropertyDetailSpecs",
    "PropertyDetails",
    "PropertyLocation",
    "PropertySearchCriteria",
    # Structured output schemas
    "PropertySearchItem",
    "PropertySearchOutputResult",
    "PropertySearchResult",
    "ROICalculation",
    "TaxBenefits",
    "UserInteraction",
    "UserPreferences",
    "UserProfile",
    "UserSession",
]
