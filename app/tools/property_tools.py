"""
Property search and analysis tools for ImmoAssist.

Provides tools for property search, investment calculations, and market analysis
specifically tailored for the German real estate market.
"""

import logging
import os
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime

from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)

# Constants for German real estate market calculations
DEFAULT_PROPERTY_APPRECIATION_RATE: float = (
    2.5  # Conservative annual appreciation percentage
)
DEFAULT_MAINTENANCE_COST_PERCENTAGE: float = (
    1.0  # Annual maintenance as percentage of property value
)
DEFAULT_MANAGEMENT_FEE_PERCENTAGE: float = (
    5.0  # Property management as percentage of rent
)
NOTARY_AND_REGISTRATION_FEE: float = 1.5  # Percentage of purchase price
REAL_ESTATE_TRANSFER_TAX: Dict[str, float] = {
    "berlin": 6.0,
    "bayern": 3.5,
    "default": 5.0,
}

# Error messages for validation
ERROR_INVALID_LOCATION = "Invalid location parameter provided"
ERROR_INVALID_PRICE_RANGE = (
    "Invalid price range format. Use format: min_price-max_price"
)
ERROR_INVALID_SIZE_RANGE = "Invalid size range format. Use format: min_size-max_size"
ERROR_API_UNAVAILABLE = "Property search API is currently unavailable"
ERROR_CALCULATION_FAILED = "Investment calculation failed due to invalid parameters"


@FunctionTool
def search_properties(
    location: str,
    property_type: str = "apartment",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
    max_results: int = 10,
) -> Dict[str, Any]:
    """
    Search available properties in the German real estate market.

    Filters properties by location, type, price range, and size criteria.
    Returns properties with investment metrics relevant for German investors.

    Args:
        location: German city or region (e.g., "Berlin", "München", "Hamburg")
        property_type: Type of property (apartment, house, commercial, land)
        min_price: Minimum price in EUR (optional)
        max_price: Maximum price in EUR (optional)
        min_size: Minimum size in square meters (optional)
        max_size: Maximum size in square meters (optional)
        max_results: Maximum number of properties to return

    Returns:
        Dictionary containing property listings with investment analysis

    Raises:
        ValueError: If location is invalid or parameters are malformed
    """
    try:
        # Validate input parameters
        if not location or not isinstance(location, str):
            raise ValueError(ERROR_INVALID_LOCATION)

        # Validate price range parameters
        if min_price is not None and (not isinstance(min_price, int) or min_price < 0):
            raise ValueError("Minimum price must be a positive integer")
        if max_price is not None and (not isinstance(max_price, int) or max_price < 0):
            raise ValueError("Maximum price must be a positive integer")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("Minimum price cannot be greater than maximum price")

        # Validate size range parameters
        if min_size is not None and (not isinstance(min_size, int) or min_size < 0):
            raise ValueError("Minimum size must be a positive integer")
        if max_size is not None and (not isinstance(max_size, int) or max_size < 0):
            raise ValueError("Maximum size must be a positive integer")
        if min_size is not None and max_size is not None and min_size > max_size:
            raise ValueError("Minimum size cannot be greater than maximum size")

        # Log search parameters
        logger.info(
            f"Searching properties in {location} with filters: "
            f"type={property_type}, price={min_price}-{max_price}, size={min_size}-{max_size}"
        )

        # Check if property search API is configured
        property_api_key = os.getenv("PROPERTY_SEARCH_API_KEY")
        if not property_api_key:
            logger.warning("Property search API not configured, returning sample data")

            # Return realistic sample properties for demo purposes
            return {
                "status": "demo",
                "message": "Using demo data. Configure PROPERTY_SEARCH_API_KEY for real searches.",
                "search_criteria": {
                    "location": location,
                    "property_type": property_type,
                    "min_price": min_price,
                    "max_price": max_price,
                    "min_size": min_size,
                    "max_size": max_size,
                },
                "properties": _get_demo_properties(location, property_type),
                "total_found": 2,
                "market_summary": {
                    "average_price_per_sqm": _get_average_price_per_sqm(location),
                    "average_yield": "3.2%",
                    "market_trend": "stable",
                    "demand_level": "high",
                },
            }

        # TODO: Implement actual property search API integration
        # Example integration point:
        # from app.services.property_api import PropertySearchClient
        # client = PropertySearchClient(api_key=property_api_key)
        # results = client.search(
        #     location=location,
        #     property_type=property_type,
        #     min_price=min_price,
        #     max_price=max_price,
        #     min_size=min_size,
        #     max_size=max_size,
        #     limit=max_results
        # )

        return {
            "status": "not_implemented",
            "message": "Property search functionality is not yet implemented.",
            "properties": [],
            "total_found": 0,
        }

    except Exception as e:
        logger.error(f"Property search failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Unable to search properties: {str(e)}",
            "properties": [],
        }


@FunctionTool
def get_property_details(
    property_id: str, include_financials: bool = True, include_neighborhood: bool = True
) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific property.

    Provides comprehensive property data including features, financials,
    and neighborhood information for investment analysis.

    Args:
        property_id: Unique identifier of the property
        include_financials: Include detailed financial projections
        include_neighborhood: Include neighborhood demographics and amenities

    Returns:
        Detailed property information with investment analysis
    """
    try:
        logger.info(f"Fetching details for property: {property_id}")

        # Check if property API is configured
        property_api_key = os.getenv("PROPERTY_SEARCH_API_KEY")
        if not property_api_key:
            return {
                "status": "error",
                "message": "Property API not configured",
                "property_id": property_id,
            }

        # TODO: Implement actual property details API call
        # from app.services.property_api import PropertySearchClient
        # client = PropertySearchClient(api_key=property_api_key)
        # details = client.get_property(property_id)

        return {
            "status": "not_implemented",
            "message": "Property details functionality is not yet implemented.",
            "property_id": property_id,
            "details": {},
        }

    except Exception as e:
        logger.error(f"Failed to get property details: {str(e)}")
        return {
            "status": "error",
            "message": f"Unable to retrieve property details: {str(e)}",
        }


@FunctionTool
def calculate_investment_return(
    purchase_price: int,
    monthly_rent: int,
    annual_expenses: Optional[int] = None,
    financing_percentage: int = 0,
    interest_rate_percent: int = 4,
    investment_period_years: int = 10,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate comprehensive investment returns for German real estate.

    Performs detailed ROI calculations including German-specific factors
    such as depreciation (AfA), tax benefits, and acquisition costs.

    Args:
        purchase_price: Total property acquisition price in EUR
        monthly_rent: Expected monthly rental income in EUR
        annual_expenses: Annual operating expenses (if None, estimated automatically)
        financing_percentage: Percentage financed (0-100)
        interest_rate_percent: Annual loan interest rate as percentage (e.g., 4 for 4.0%)
        investment_period_years: Investment holding period
        location: Property location for tax calculation

    Returns:
        Comprehensive investment analysis including:
        - Yield calculations (gross, net, cash-on-cash)
        - Cash flow projections
        - Tax implications
        - Total return estimates

    Raises:
        ValueError: If input parameters are invalid or out of range
    """
    try:
        # Validate input parameters
        if purchase_price <= 0:
            raise ValueError("Purchase price must be greater than 0")
        if monthly_rent <= 0:
            raise ValueError("Monthly rent must be greater than 0")
        if financing_percentage < 0 or financing_percentage > 100:
            raise ValueError("Financing percentage must be between 0 and 100")
        if interest_rate_percent < 0:
            raise ValueError("Interest rate must be greater than or equal to 0")
        if investment_period_years <= 0:
            raise ValueError("Investment period must be greater than 0")

        # Convert percentage to decimal for calculations
        interest_rate = interest_rate_percent / 100.0
        financing_ratio = financing_percentage / 100.0

        logger.info(
            f"Calculating investment returns for €{purchase_price:,} property, "
            f"rent: €{monthly_rent}/month"
        )

        # Calculate acquisition costs (German specific)
        transfer_tax_rate = REAL_ESTATE_TRANSFER_TAX.get(
            location.lower() if location else "default",
            REAL_ESTATE_TRANSFER_TAX["default"],
        )
        acquisition_costs = purchase_price * (
            (transfer_tax_rate + NOTARY_AND_REGISTRATION_FEE) / 100
        )
        total_investment = purchase_price + acquisition_costs

        # Annual income calculations
        annual_rent = monthly_rent * 12

        # Estimate annual expenses if not provided
        if annual_expenses is None:
            maintenance = purchase_price * (DEFAULT_MAINTENANCE_COST_PERCENTAGE / 100)
            management = annual_rent * (DEFAULT_MANAGEMENT_FEE_PERCENTAGE / 100)
            annual_expenses = maintenance + management
            logger.debug(f"Estimated annual expenses: €{annual_expenses:,.0f}")

        net_annual_income = annual_rent - annual_expenses

        # Financing calculations
        if financing_percentage > 0:
            loan_amount = purchase_price * (financing_percentage / 100)
            equity_required = total_investment - loan_amount
            annual_interest = loan_amount * (interest_rate / 100)

            # Simplified loan amortization (1% annual)
            annual_principal = loan_amount * 0.01
            annual_debt_service = annual_interest + annual_principal

            net_cash_flow = net_annual_income - annual_debt_service
        else:
            loan_amount = 0
            equity_required = total_investment
            annual_interest = 0
            annual_principal = 0
            annual_debt_service = 0
            net_cash_flow = net_annual_income

        # German tax benefits calculation
        annual_depreciation = purchase_price * 0.02  # 2% AfA for residential
        tax_deductible_expenses = (
            annual_expenses + annual_interest + annual_depreciation
        )

        # Yield calculations
        gross_yield = (annual_rent / total_investment) * 100
        net_yield = (net_annual_income / total_investment) * 100
        cash_on_cash_return = (
            (net_cash_flow / equity_required) * 100 if equity_required > 0 else 0
        )

        # Property value projection
        appreciation_rate = DEFAULT_PROPERTY_APPRECIATION_RATE / 100
        future_property_value = purchase_price * (
            (1 + appreciation_rate) ** investment_period_years
        )

        # Total return calculation
        total_rental_income = net_cash_flow * investment_period_years
        capital_gain = future_property_value - purchase_price
        loan_paydown = (
            annual_principal * investment_period_years
            if financing_percentage > 0
            else 0
        )
        total_return = total_rental_income + capital_gain + loan_paydown

        # Annualized return
        if equity_required > 0:
            total_return_rate = (
                (total_return + equity_required) / equity_required
            ) ** (1 / investment_period_years) - 1
            annualized_return = total_return_rate * 100
        else:
            annualized_return = 0

        return {
            "status": "success",
            "investment_summary": {
                "purchase_price": round(purchase_price, 2),
                "acquisition_costs": round(acquisition_costs, 2),
                "total_investment": round(total_investment, 2),
                "equity_required": round(equity_required, 2),
                "loan_amount": round(loan_amount, 2),
                "location": location or "Germany",
            },
            "income_analysis": {
                "monthly_rent": round(monthly_rent, 2),
                "annual_rent": round(annual_rent, 2),
                "annual_expenses": round(annual_expenses, 2),
                "net_annual_income": round(net_annual_income, 2),
            },
            "financing_details": {
                "financing_percentage": financing_percentage,
                "interest_rate": interest_rate,
                "annual_interest": round(annual_interest, 2),
                "annual_principal": round(annual_principal, 2),
                "annual_debt_service": round(annual_debt_service, 2),
            },
            "yield_metrics": {
                "gross_yield_percent": round(gross_yield, 2),
                "net_yield_percent": round(net_yield, 2),
                "cash_on_cash_return_percent": round(cash_on_cash_return, 2),
                "annual_cash_flow": round(net_cash_flow, 2),
            },
            "tax_benefits": {
                "annual_depreciation_afa": round(annual_depreciation, 2),
                "tax_deductible_expenses": round(tax_deductible_expenses, 2),
                "transfer_tax_rate": transfer_tax_rate,
            },
            "projections": {
                "investment_period_years": investment_period_years,
                "future_property_value": round(future_property_value, 2),
                "total_rental_income": round(total_rental_income, 2),
                "capital_gain": round(capital_gain, 2),
                "loan_paydown": round(loan_paydown, 2),
                "total_return": round(total_return, 2),
                "annualized_return_percent": round(annualized_return, 2),
            },
            "assumptions": {
                "appreciation_rate_percent": DEFAULT_PROPERTY_APPRECIATION_RATE,
                "maintenance_cost_percent": DEFAULT_MAINTENANCE_COST_PERCENTAGE,
                "management_fee_percent": DEFAULT_MANAGEMENT_FEE_PERCENTAGE,
            },
        }

    except Exception as e:
        logger.error(f"Investment calculation failed: {str(e)}")
        return {
            "status": "error",
            "message": f"Unable to calculate investment returns: {str(e)}",
        }


def _get_demo_properties(location: str, property_type: str) -> List[Dict[str, Any]]:
    """Generate realistic demo properties for testing."""
    base_properties = [
        {
            "id": f"demo_{datetime.now().timestamp():.0f}_1",
            "title": f"Modern {property_type.title()} in Prime Location",
            "location": f"{location} - City Center",
            "property_type": property_type,
            "price": 450000,
            "size_sqm": 75,
            "rooms": 3,
            "year_built": 2020,
            "energy_efficiency": "A+",
            "features": ["Balcony", "Elevator", "Underground Parking", "Floor Heating"],
            "investment_metrics": {
                "price_per_sqm": 6000,
                "gross_yield": "3.2%",
                "estimated_rent": 1200,
            },
        },
        {
            "id": f"demo_{datetime.now().timestamp():.0f}_2",
            "title": f"Renovated {property_type.title()} with Garden Access",
            "location": f"{location} - Residential Area",
            "property_type": property_type,
            "price": 380000,
            "size_sqm": 85,
            "rooms": 3.5,
            "year_built": 1995,
            "energy_efficiency": "C",
            "features": ["Garden", "Renovated 2022", "Storage Room", "Bike Room"],
            "investment_metrics": {
                "price_per_sqm": 4471,
                "gross_yield": "3.6%",
                "estimated_rent": 1140,
            },
        },
    ]

    return base_properties


def _get_average_price_per_sqm(location: str) -> float:
    """Get average price per square meter for major German cities."""
    # Approximate market data (should be replaced with real-time data)
    city_prices = {
        "münchen": 9500,
        "munich": 9500,
        "frankfurt": 6500,
        "hamburg": 6000,
        "berlin": 5500,
        "stuttgart": 5200,
        "düsseldorf": 5000,
        "cologne": 4800,
        "köln": 4800,
        "leipzig": 3200,
        "dresden": 3500,
    }

    return city_prices.get(location.lower(), 4500)  # Default average


# Export all tools
__all__ = ["search_properties", "get_property_details", "calculate_investment_return"]
