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
def calculate_investment_return(term: str) -> str:
    """Поясняет финансовые термины и принципы расчёта доходности, не производя никаких вычислений."""
    explanations = {
        "митрендите": "Митрендите (Mietrendite) — это показатель доходности недвижимости, рассчитываемый как отношение годового дохода от аренды к стоимости объекта. Он помогает инвестору понять, насколько эффективно вложены средства.",
        "tilgung": "Тильгунг (Tilgung) — это процесс погашения основного долга по ипотечному кредиту. Обычно ежемесячный платёж по кредиту состоит из процентов и части суммы основного долга (Tilgung). Чем выше доля Tilgung, тем быстрее уменьшается задолженность.",
        "sonder-afa": "Sonder-AfA — это специальная ускоренная амортизация для новых объектов недвижимости в Германии. Она позволяет списывать 5% стоимости объекта ежегодно в течение первых лет, что существенно снижает налоговую нагрузку инвестора.",
        # Можно добавить другие термины по аналогии
    }
    key = term.strip().lower()
    return explanations.get(key, f"Пояснение по термину '{term}' отсутствует. Уточните, пожалуйста, что именно вас интересует из финансовых понятий.") 