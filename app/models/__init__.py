"""
Domain models for ImmoAssist enterprise system.

This module exports all domain models used across the application,
following clean architecture principles with clear separation of concerns.
"""

from .property import (
    Property,
    PropertyLocation,
    PropertySearchCriteria,
    PropertySearchResult
)

from .financial import (
    FinancialCalculation,
    LoanDetails,
    InvestmentMetrics,
    TaxBenefits,
    ROICalculation
)

from .user import (
    UserProfile,
    UserPreferences,
    UserSession,
    ConversationHistory,
    UserInteraction
)

# Structured output schemas for tools and agents
from .output_schemas import (
    # Property outputs
    PropertySearchItem,
    PropertySearchResult as PropertySearchOutputResult,
    PropertyDetails,
    PropertyDetailLocation,
    PropertyDetailSpecs,
    PropertyDetailFinancials,
    
    # Financial calculation outputs
    CalculationSummary,
    GermanTaxBenefits,
    InvestmentRecommendation,
    InvestmentCalculationResult,
    
    # Knowledge base outputs
    KnowledgeSearchResult,
    ProcessGuide,
    ProcessGuideStep,
    
    # Integration outputs
    HeyGenResponse,
    ElevenLabsResponse,
    
    # Error handling
    AgentError
)

__all__ = [
    # Domain models
    "Property",
    "PropertyLocation", 
    "PropertySearchCriteria",
    "PropertySearchResult",
    "FinancialCalculation",
    "LoanDetails",
    "InvestmentMetrics", 
    "TaxBenefits",
    "ROICalculation",
    "UserProfile",
    "UserPreferences",
    "UserSession",
    "ConversationHistory",
    "UserInteraction",
    
    # Structured output schemas  
    "PropertySearchItem",
    "PropertySearchOutputResult",
    "PropertyDetails",
    "PropertyDetailLocation",
    "PropertyDetailSpecs", 
    "PropertyDetailFinancials",
    "CalculationSummary",
    "GermanTaxBenefits",
    "InvestmentRecommendation",
    "InvestmentCalculationResult",
    "KnowledgeSearchResult",
    "ProcessGuide",
    "ProcessGuideStep",
    "HeyGenResponse",
    "ElevenLabsResponse",
    "AgentError"
] 