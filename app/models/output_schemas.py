"""
Structured output schemas for ImmoAssist tools and agents.

Following gemini-fullstack best practices with Pydantic models
for type-safe, validated outputs.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# === PROPERTY SEARCH OUTPUTS ===

class PropertySearchItem(BaseModel):
    """Individual property item in search results."""
    
    id: str = Field(description="Unique property identifier")
    title: str = Field(description="Property title/name")
    location: str = Field(description="City and region")
    price: int = Field(description="Purchase price in EUR")
    size_sqm: int = Field(description="Size in square meters")
    rooms: int = Field(description="Number of rooms")
    energy_class: str = Field(description="Energy efficiency class")
    monthly_rental_income: int = Field(description="Expected monthly rental income in EUR")
    expected_roi: float = Field(description="Expected ROI percentage")


class PropertySearchResult(BaseModel):
    """Search results for property queries."""
    
    properties: List[PropertySearchItem] = Field(description="List of found properties")
    total_count: int = Field(description="Total number of matching properties")
    search_criteria: Dict[str, Any] = Field(description="Applied search filters")


class PropertyDetailLocation(BaseModel):
    """Detailed location information."""
    
    city: str = Field(description="City name")
    district: str = Field(description="District/neighborhood")
    address: str = Field(description="Street address")
    postal_code: Optional[str] = Field(default=None, description="Postal code")


class PropertyDetailSpecs(BaseModel):
    """Property specifications."""
    
    size_sqm: int = Field(description="Size in square meters")
    rooms: int = Field(description="Number of rooms")
    energy_class: str = Field(description="Energy efficiency class")
    completion_year: int = Field(description="Year of completion")
    has_balcony: Optional[bool] = Field(default=None, description="Has balcony/terrace")
    has_parking: Optional[bool] = Field(default=None, description="Has parking space")


class PropertyDetailFinancials(BaseModel):
    """Financial details of property."""
    
    monthly_rental_income: int = Field(description="Expected monthly rental income in EUR")
    expected_roi: float = Field(description="Expected ROI percentage")
    rental_guarantee_months: Optional[int] = Field(default=None, description="Rental guarantee duration")
    management_fee_monthly: Optional[int] = Field(default=None, description="Monthly management fee")


class PropertyDetails(BaseModel):
    """Detailed property information."""
    
    id: str = Field(description="Property ID")
    title: str = Field(description="Property title")
    price: int = Field(description="Purchase price in EUR")
    location: PropertyDetailLocation = Field(description="Location details")
    specs: PropertyDetailSpecs = Field(description="Property specifications")
    financials: PropertyDetailFinancials = Field(description="Financial information")


# === FINANCIAL CALCULATION OUTPUTS ===

class CalculationSummary(BaseModel):
    """Summary of investment calculation."""
    
    purchase_price: int = Field(description="Total purchase price in EUR")
    down_payment: int = Field(description="Down payment amount in EUR")
    loan_amount: int = Field(description="Loan amount in EUR")
    monthly_payment: float = Field(description="Monthly loan payment in EUR")
    monthly_net_income: float = Field(description="Monthly net income without tax benefits")
    monthly_net_with_tax: float = Field(description="Monthly net income with tax benefits")


class GermanTaxBenefits(BaseModel):
    """German real estate tax benefits."""
    
    annual_depreciation: float = Field(description="Annual depreciation amount (5% for new construction)")
    annual_tax_savings: float = Field(description="Annual tax savings from depreciation")
    monthly_tax_savings: float = Field(description="Monthly tax savings")
    special_depreciation_rate: float = Field(description="Applied depreciation rate (5% for new buildings)")


class InvestmentRecommendation(BaseModel):
    """Investment recommendation with analysis."""
    
    recommended: bool = Field(description="Whether investment is recommended")
    roi_percentage: float = Field(description="Annual ROI percentage")
    payback_period_years: Optional[float] = Field(default=None, description="Payback period in years")
    risk_level: Literal["low", "medium", "high"] = Field(default="medium", description="Investment risk level")
    key_benefits: List[str] = Field(default_factory=list, description="Key investment benefits")
    risks: List[str] = Field(default_factory=list, description="Potential risks")


class InvestmentCalculationResult(BaseModel):
    """Complete investment calculation result."""
    
    summary: CalculationSummary = Field(description="Calculation summary")
    tax_benefits: GermanTaxBenefits = Field(description="German tax benefits")
    recommendation: InvestmentRecommendation = Field(description="Investment recommendation")
    calculated_at: datetime = Field(default_factory=datetime.now, description="Calculation timestamp")


# === KNOWLEDGE BASE OUTPUTS ===

class KnowledgeSearchResult(BaseModel):
    """Result from knowledge base search."""
    
    query: str = Field(description="Original search query")
    results: List[str] = Field(description="Found knowledge base entries")
    source_type: Literal["faq", "handbook", "process"] = Field(description="Type of knowledge source")
    confidence_score: Optional[float] = Field(default=None, description="Search confidence score")


class ProcessGuideStep(BaseModel):
    """Single step in a process guide."""
    
    step_number: int = Field(description="Step number")
    title: str = Field(description="Step title")
    description: str = Field(description="Step description")
    required_documents: Optional[List[str]] = Field(default=None, description="Required documents")
    estimated_duration: Optional[str] = Field(default=None, description="Estimated duration")


class ProcessGuide(BaseModel):
    """Complete process guide."""
    
    process_name: str = Field(description="Name of the process")
    overview: str = Field(description="Process overview")
    steps: List[ProcessGuideStep] = Field(description="Process steps")
    total_duration: Optional[str] = Field(default=None, description="Total estimated duration")
    important_notes: Optional[List[str]] = Field(default=None, description="Important notes")


# === INTEGRATION OUTPUTS ===

class HeyGenResponse(BaseModel):
    """Response from HeyGen avatar generation."""
    
    success: bool = Field(description="Whether the request was successful")
    avatar_url: Optional[str] = Field(default=None, description="Generated avatar video URL")
    message_id: Optional[str] = Field(default=None, description="Message ID for tracking")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


class ElevenLabsResponse(BaseModel):
    """Response from ElevenLabs audio generation."""
    
    success: bool = Field(description="Whether the request was successful")
    audio_url: Optional[str] = Field(default=None, description="Generated audio URL")
    duration_seconds: Optional[float] = Field(default=None, description="Audio duration")
    voice_id: Optional[str] = Field(default=None, description="Used voice ID")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")


# === ERROR OUTPUTS ===

class AgentError(BaseModel):
    """Structured error output for agent failures."""
    
    error_type: Literal["validation", "api", "timeout", "internal"] = Field(description="Type of error")
    error_code: str = Field(description="Error code for identification")
    message: str = Field(description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")
    recoverable: bool = Field(description="Whether the error is recoverable") 