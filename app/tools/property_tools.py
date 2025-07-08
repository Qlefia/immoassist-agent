"""Property tools for ImmoAssist enterprise system."""

from typing import Optional

from google.adk.tools import FunctionTool

from ..models.output_schemas import (
    CalculationSummary,
    GermanTaxBenefits,
    InvestmentCalculationResult,
    InvestmentRecommendation,
    PropertyDetailFinancials,
    PropertyDetailLocation,
    PropertyDetails,
    PropertyDetailSpecs,
    PropertySearchItem,
    PropertySearchResult,
)


@FunctionTool
def search_properties(
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    property_type: Optional[str] = None,
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
            expected_roi=5.2,
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
            expected_roi=4.8,
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
            expected_roi=5.0,
        ),
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
        properties=filtered, total_count=len(filtered), search_criteria=search_criteria
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
                postal_code="80802",
            ),
            specs=PropertyDetailSpecs(
                size_sqm=65,
                rooms=2,
                energy_class="A+",
                completion_year=2024,
                has_balcony=True,
                has_parking=True,
            ),
            financials=PropertyDetailFinancials(
                monthly_rental_income=1200,
                expected_roi=5.2,
                rental_guarantee_months=12,
                management_fee_monthly=80,
            ),
        ),
        "prop_ber_002": PropertyDetails(
            id="prop_ber_002",
            title="3-Zimmer-Wohnung in Berlin",
            price=320000,
            location=PropertyDetailLocation(
                city="Berlin",
                district="Prenzlauer Berg",
                address="Kastanienallee 45",
                postal_code="10119",
            ),
            specs=PropertyDetailSpecs(
                size_sqm=85,
                rooms=3,
                energy_class="A+",
                completion_year=2024,
                has_balcony=True,
                has_parking=False,
            ),
            financials=PropertyDetailFinancials(
                monthly_rental_income=1450,
                expected_roi=4.8,
                rental_guarantee_months=6,
                management_fee_monthly=95,
            ),
        ),
    }

    if property_id not in property_details_map:
        raise ValueError(f"Property with ID {property_id} not found")

    return property_details_map[property_id]


@FunctionTool
def calculate_investment_return(
    purchase_price: int,
    down_payment: int,
    monthly_rental_income: int,
    interest_rate: float = 4.5,
    loan_term_years: int = 30,
) -> InvestmentCalculationResult:
    """Calculate investment return and provide detailed financial analysis."""

    # Calculate loan amount
    loan_amount = purchase_price - down_payment

    # Calculate monthly payment (simplified)
    monthly_rate = interest_rate / 100 / 12
    total_payments = loan_term_years * 12
    monthly_payment = (
        loan_amount
        * (monthly_rate * (1 + monthly_rate) ** total_payments)
        / ((1 + monthly_rate) ** total_payments - 1)
    )

    # Calculate annual depreciation (5% for new construction)
    annual_depreciation = purchase_price * 0.05
    annual_tax_savings = annual_depreciation * 0.42  # Assuming 42% tax rate
    monthly_tax_savings = annual_tax_savings / 12

    # Calculate net income
    monthly_net_income = monthly_rental_income - monthly_payment
    monthly_net_with_tax = monthly_net_income + monthly_tax_savings

    # Calculate ROI
    annual_rental_income = monthly_rental_income * 12
    roi_percentage = (annual_rental_income / purchase_price) * 100

    # Determine recommendation
    recommended = roi_percentage >= 4.0 and monthly_net_with_tax > 0
    risk_level = (
        "low"
        if roi_percentage >= 5.0
        else "medium"
        if roi_percentage >= 4.0
        else "high"
    )

    # Calculate payback period
    payback_period = None
    if monthly_net_with_tax > 0:
        payback_period = down_payment / (monthly_net_with_tax * 12)

    return InvestmentCalculationResult(
        summary=CalculationSummary(
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_amount=loan_amount,
            monthly_payment=monthly_payment,
            monthly_net_income=monthly_net_income,
            monthly_net_with_tax=monthly_net_with_tax,
        ),
        tax_benefits=GermanTaxBenefits(
            annual_depreciation=annual_depreciation,
            annual_tax_savings=annual_tax_savings,
            monthly_tax_savings=monthly_tax_savings,
            special_depreciation_rate=5.0,
        ),
        recommendation=InvestmentRecommendation(
            recommended=recommended,
            roi_percentage=roi_percentage,
            payback_period_years=payback_period,
            risk_level=risk_level,
            key_benefits=[
                "5% Sonder-AfA для новых объектов",
                "Высокая энергоэффективность (A+)",
                "Гарантированная аренда",
                "Низкие эксплуатационные расходы",
            ],
            risks=[
                "Рыночные колебания цен",
                "Изменения в налоговом законодательстве",
                "Возможные задержки в строительстве",
            ],
        ),
    )
