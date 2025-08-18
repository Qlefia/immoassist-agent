"""
Domain models for ImmoAssist

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
    # Financial calculation outputs
    CalculationSummary,
    GermanTaxBenefits,
    # Property outputs
    PropertyDetailFinancials,
    PropertyDetailLocation,
    PropertyDetails,
    PropertyDetailSpecs,
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
    "CalculationSummary",
    "ConversationHistory",
    "FinancialCalculation",
    "GermanTaxBenefits",
    "InvestmentMetrics",
    "LoanDetails",
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
