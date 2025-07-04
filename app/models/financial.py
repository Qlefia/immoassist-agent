"""Financial domain models for ImmoAssist."""

from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from pydantic import BaseModel, Field


class LoanDetails(BaseModel):
    """Loan details for property financing."""
    loan_amount: Decimal = Field(..., gt=0)
    interest_rate: Decimal = Field(..., gt=0)
    term_years: int = Field(..., gt=0)
    monthly_payment: Decimal = Field(..., gt=0)
    
    class Config:
        frozen = True


class TaxBenefits(BaseModel):
    """Tax benefits for property investment."""
    annual_depreciation: Decimal = Field(..., ge=0)
    special_depreciation: Decimal = Field(default=Decimal("0"), ge=0)
    annual_tax_savings: Decimal = Field(..., ge=0)
    
    class Config:
        frozen = True


class InvestmentMetrics(BaseModel):
    """Investment performance metrics."""
    gross_yield_percent: Decimal = Field(..., ge=0)
    net_yield_percent: Decimal = Field(..., ge=0)
    roi_percent: Decimal = Field(..., ge=0)
    payback_period_years: Decimal = Field(..., gt=0)
    
    class Config:
        frozen = True


class FinancialCalculation(BaseModel):
    """Complete financial calculation for property investment."""
    property_id: str
    purchase_price: Decimal = Field(..., gt=0)
    down_payment: Decimal = Field(..., ge=0)
    monthly_rental_income: Decimal = Field(..., gt=0)
    monthly_costs: Decimal = Field(..., ge=0)
    
    # Components
    loan_details: LoanDetails
    tax_benefits: TaxBenefits
    metrics: InvestmentMetrics
    
    # Summary
    monthly_net_income: Decimal
    total_roi_10_years: Decimal
    recommended: bool
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True


class ROICalculation(BaseModel):
    """ROI calculation result."""
    initial_investment: Decimal
    annual_return: Decimal
    roi_percentage: Decimal
    calculation_date: datetime = Field(default_factory=datetime.now)
    
    class Config:
        frozen = True 