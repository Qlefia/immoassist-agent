"""
Output schema models for ImmoAssist.

Pydantic models defining structured outputs for property data,
investment calculations, and external service responses.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field


class PropertySearchItem(BaseModel):
    """Individual property item in search results."""

    id: str = Field(description="Unique property identifier")
    title: str = Field(description="Property title or description")
    location: str = Field(description="Property location (city, district)")
    price: int = Field(description="Property price in euros")
    size_sqm: int = Field(description="Property size in square meters")
    rooms: int = Field(description="Number of rooms")
    energy_class: str = Field(description="Energy efficiency class (A+ to H)")
    monthly_rental_income: int = Field(
        description="Expected monthly rental income in euros"
    )
    expected_roi: float = Field(
        description="Expected return on investment as percentage"
    )


class PropertySearchResult(BaseModel):
    """Complete property search result with filters applied."""

    properties: List[PropertySearchItem] = Field(
        description="List of matching properties"
    )
    total_count: int = Field(description="Total number of properties found")
    search_criteria: dict = Field(description="Applied search filters and criteria")


class PropertyDetailSpecs(BaseModel):
    """Detailed property specifications."""

    size_sqm: int = Field(description="Property size in square meters")
    rooms: int = Field(description="Total number of rooms")
    energy_class: str = Field(description="Energy efficiency classification")
    completion_year: int = Field(description="Year of construction completion")
    has_balcony: bool = Field(description="Whether property has balcony or terrace")
    has_parking: bool = Field(description="Whether parking space is included")


class PropertyDetailLocation(BaseModel):
    """Detailed property location information."""

    city: str = Field(description="City name")
    district: str = Field(description="District or neighborhood")
    address: str = Field(description="Full street address")
    postal_code: str = Field(description="Postal code")


class PropertyDetailFinancials(BaseModel):
    """Financial details for property investment."""

    monthly_rental_income: int = Field(description="Expected monthly rental income")
    expected_roi: float = Field(description="Expected return on investment percentage")
    rental_guarantee_months: int = Field(
        description="Number of months with rental guarantee"
    )
    management_fee_monthly: int = Field(description="Monthly property management fee")


class PropertyDetails(BaseModel):
    """Complete detailed property information."""

    id: str = Field(description="Unique property identifier")
    title: str = Field(description="Property title")
    price: int = Field(description="Property price in euros")
    location: PropertyDetailLocation = Field(description="Location details")
    specs: PropertyDetailSpecs = Field(description="Property specifications")
    financials: PropertyDetailFinancials = Field(description="Financial information")


class CalculationSummary(BaseModel):
    """Summary of investment calculation inputs and basic outputs."""

    purchase_price: int = Field(description="Total property purchase price")
    down_payment: int = Field(description="Initial down payment amount")
    loan_amount: int = Field(description="Financed loan amount")
    monthly_payment: float = Field(description="Monthly loan payment")
    monthly_net_income: float = Field(
        description="Net monthly income before tax benefits"
    )
    monthly_net_with_tax: float = Field(
        description="Net monthly income including tax savings"
    )


class GermanTaxBenefits(BaseModel):
    """German tax benefits for real estate investment."""

    annual_depreciation: float = Field(description="Annual depreciation amount")
    annual_tax_savings: float = Field(
        description="Annual tax savings from depreciation"
    )
    monthly_tax_savings: float = Field(description="Monthly tax savings")
    special_depreciation_rate: float = Field(
        description="Special depreciation rate percentage"
    )


class InvestmentRecommendation(BaseModel):
    """Investment recommendation with risk assessment."""

    recommended: bool = Field(description="Whether investment is recommended")
    roi_percentage: float = Field(description="Return on investment percentage")
    payback_period_years: Optional[float] = Field(description="Payback period in years")
    risk_level: str = Field(description="Risk assessment level (low, medium, high)")
    key_benefits: List[str] = Field(description="List of key investment benefits")
    risks: List[str] = Field(description="List of potential investment risks")


class InvestmentCalculationResult(BaseModel):
    """Complete investment calculation result with recommendations."""

    summary: CalculationSummary = Field(description="Calculation summary")
    tax_benefits: GermanTaxBenefits = Field(description="German tax benefits")
    recommendation: InvestmentRecommendation = Field(
        description="Investment recommendation"
    )


class RagSource(BaseModel):
    """RAG knowledge source with citation information."""

    title: str = Field(description="Source document title")
    link: str = Field(description="Source document URL or reference")


class RagResponse(BaseModel):
    """RAG search response with answer and sources."""

    answer: str = Field(description="Generated answer from knowledge base")
    sources: List[RagSource] = Field(description="List of source documents cited")


class ElevenLabsResponse(BaseModel):
    """Response from ElevenLabs text-to-speech service."""

    success: bool = Field(description="Whether audio generation was successful")
    audio_url: Optional[str] = Field(description="URL to generated audio file")
    duration_seconds: Optional[float] = Field(description="Audio duration in seconds")
    voice_id: Optional[str] = Field(description="Voice identifier used")
    error_message: Optional[str] = Field(
        description="Error message if generation failed"
    )


class ConversationAnalysis(BaseModel):
    """Analysis result from conversation context analysis."""

    interaction_type: str = Field(description="Type of user interaction")
    conversation_phase: str = Field(description="Current conversation phase")
    emotional_tone: str = Field(description="Detected emotional tone")
    topics_mentioned: List[str] = Field(description="Topics mentioned in input")
    user_preferences: dict = Field(description="Extracted user preferences")
    response_recommendations: List[str] = Field(
        description="Recommended response strategies"
    )


class MemoryOperation(BaseModel):
    """Result of memory storage or retrieval operation."""

    status: str = Field(description="Operation status (success, error, empty)")
    message: str = Field(description="Status message or description")
    data: Optional[Union[dict, list, str]] = Field(
        description="Retrieved or stored data"
    )


class MarketInsight(BaseModel):
    """Market analysis and insights for specific location."""

    location: str = Field(description="Geographic location analyzed")
    property_type: str = Field(description="Type of property analyzed")
    market_metrics: dict = Field(description="Current market metrics and trends")
    investment_outlook: dict = Field(description="Investment potential and forecasts")
    risk_factors: List[str] = Field(description="Identified market risk factors")
