"""Property tools for ImmoAssist enterprise system."""

from typing import Optional
from google.adk.tools import FunctionTool
from ..config import config
from ..models.output_schemas import (
    PropertySearchResult,
    PropertySearchItem,
    PropertyDetails,
    PropertyDetailLocation,
    PropertyDetailSpecs,
    PropertyDetailFinancials,
    InvestmentCalculationResult,
    CalculationSummary,
    GermanTaxBenefits,
    InvestmentRecommendation
)


@FunctionTool
def search_properties(
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    property_type: Optional[str] = None
) -> PropertySearchResult:
    """Search available properties by criteria."""
    
    # Sample data - TODO: Replace with real API integration
    sample_properties = [
        PropertySearchItem(
            id="prop_muc_001",
            title="Moderne 2-Zimmer-Wohnung in München",
            location="München, Bayern",
            price=285000,
            size_sqm=65,
            rooms=2,
            energy_class="A+",
            monthly_rental_income=1200,
            expected_roi=5.2
        ),
        PropertySearchItem(
            id="prop_ber_002", 
            title="3-Zimmer-Wohnung in Berlin",
            location="Berlin, Berlin",
            price=320000,
            size_sqm=85,
            rooms=3,
            energy_class="A+",
            monthly_rental_income=1450,
            expected_roi=4.8
        ),
        PropertySearchItem(
            id="prop_ham_003",
            title="2-Zimmer-Neubau in Hamburg",
            location="Hamburg, Hamburg",
            price=295000,
            size_sqm=70,
            rooms=2,
            energy_class="A+",
            monthly_rental_income=1300,
            expected_roi=5.0
        )
    ]
    
    # Apply filters
    filtered = sample_properties
    if location:
        filtered = [p for p in filtered if location.lower() in p.location.lower()]
    if min_price:
        filtered = [p for p in filtered if p.price >= min_price]
    if max_price:
        filtered = [p for p in filtered if p.price <= max_price]
    
    # Build search criteria
    search_criteria = {}
    if location:
        search_criteria["location"] = location
    if min_price:
        search_criteria["min_price"] = min_price
    if max_price:
        search_criteria["max_price"] = max_price
    if property_type:
        search_criteria["property_type"] = property_type
    
    return PropertySearchResult(
        properties=filtered,
        total_count=len(filtered),
        search_criteria=search_criteria
    )


@FunctionTool
def get_property_details(property_id: str) -> PropertyDetails:
    """Get detailed property information."""
    
    # Sample data - TODO: Replace with real database integration
    property_details_map = {
        "prop_muc_001": PropertyDetails(
            id="prop_muc_001",
            title="Moderne 2-Zimmer-Wohnung in München",
            price=285000,
            location=PropertyDetailLocation(
                city="München",
                district="Schwabing",
                address="Leopoldstraße 125",
                postal_code="80802"
            ),
            specs=PropertyDetailSpecs(
                size_sqm=65,
                rooms=2,
                energy_class="A+",
                completion_year=2024,
                has_balcony=True,
                has_parking=True
            ),
            financials=PropertyDetailFinancials(
                monthly_rental_income=1200,
                expected_roi=5.2,
                rental_guarantee_months=12,
                management_fee_monthly=80
            )
        ),
        "prop_ber_002": PropertyDetails(
            id="prop_ber_002",
            title="3-Zimmer-Wohnung in Berlin",
            price=320000,
            location=PropertyDetailLocation(
                city="Berlin",
                district="Prenzlauer Berg",
                address="Kastanienallee 45",
                postal_code="10119"
            ),
            specs=PropertyDetailSpecs(
                size_sqm=85,
                rooms=3,
                energy_class="A+",
                completion_year=2024,
                has_balcony=True,
                has_parking=False
            ),
            financials=PropertyDetailFinancials(
                monthly_rental_income=1450,
                expected_roi=4.8,
                rental_guarantee_months=6,
                management_fee_monthly=95
            )
        )
    }
    
    if property_id not in property_details_map:
        raise ValueError(f"Property with ID {property_id} not found")
    
    return property_details_map[property_id]


@FunctionTool 
def calculate_investment_return(
    purchase_price: int,
    down_payment: int,
    monthly_rental_income: int,
    monthly_costs: int = 200,
    loan_interest_rate: float = 3.5,
    user_tax_rate: float = 0.42
) -> InvestmentCalculationResult:
    """Calculate investment return for German real estate."""
    
    # Validation
    if purchase_price <= 0:
        raise ValueError("Purchase price must be positive")
    if down_payment <= 0 or down_payment >= purchase_price:
        raise ValueError("Down payment must be positive and less than purchase price")
    if monthly_rental_income <= 0:
        raise ValueError("Monthly rental income must be positive")
    
    # Basic calculations
    loan_amount = purchase_price - down_payment
    monthly_interest_rate = loan_interest_rate / 100 / 12
    
    # Monthly payment calculation (simplified annuity formula)
    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * monthly_interest_rate * (1 + monthly_interest_rate)**360 / ((1 + monthly_interest_rate)**360 - 1)
    else:
        monthly_payment = loan_amount / 360  # No interest case
    
    # Cash flow
    monthly_net = monthly_rental_income - monthly_payment - monthly_costs
    
    # German tax benefits (5% special depreciation for new construction)
    annual_depreciation = purchase_price * config.special_depreciation_rate
    annual_tax_savings = annual_depreciation * user_tax_rate
    monthly_tax_savings = annual_tax_savings / 12
    
    monthly_net_with_tax = monthly_net + monthly_tax_savings
    
    # ROI calculation
    annual_net_with_tax = monthly_net_with_tax * 12
    roi_percentage = (annual_net_with_tax / down_payment) * 100 if down_payment > 0 else 0
    
    # Payback period
    payback_period = down_payment / (monthly_net_with_tax * 12) if monthly_net_with_tax > 0 else None
    
    # Risk assessment
    if roi_percentage > 6:
        risk_level = "low"
        key_benefits = ["Hohe Rendite", "Steuervorteile durch 5% AfA", "Neue Energieeffizienz A+"]
        risks = ["Marktrisiko", "Leerstandsrisiko"]
    elif roi_percentage > 3:
        risk_level = "medium"
        key_benefits = ["Solide Rendite", "Steuervorteile", "Inflationsschutz"]
        risks = ["Marktvolatilität", "Zinssteigerungsrisiko", "Instandhaltungskosten"]
    else:
        risk_level = "high"
        key_benefits = ["Steuervorteile", "Sachwert"]
        risks = ["Niedrige Rendite", "Hohe Finanzierungskosten", "Marktrisiko"]
    
    return InvestmentCalculationResult(
        summary=CalculationSummary(
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_amount=loan_amount,
            monthly_payment=round(monthly_payment, 2),
            monthly_net_income=round(monthly_net, 2),
            monthly_net_with_tax=round(monthly_net_with_tax, 2)
        ),
        tax_benefits=GermanTaxBenefits(
            annual_depreciation=annual_depreciation,
            annual_tax_savings=round(annual_tax_savings, 2),
            monthly_tax_savings=round(monthly_tax_savings, 2),
            special_depreciation_rate=config.special_depreciation_rate
        ),
        recommendation=InvestmentRecommendation(
            recommended=monthly_net_with_tax > 0,
            roi_percentage=round(roi_percentage, 2),
            payback_period_years=round(payback_period, 1) if payback_period else None,
            risk_level=risk_level,
            key_benefits=key_benefits,
            risks=risks
        )
    ) 