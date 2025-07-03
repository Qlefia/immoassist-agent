"""
Property management tools for ImmoAssist.

This module contains tools for searching properties, retrieving property details,
and calculating investment returns for German real estate investments.
"""

from typing import Dict, List, Optional
from google.adk.tools import FunctionTool
import json

@FunctionTool
def search_properties(
    location: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    property_type: Optional[str] = None
) -> str:
    """
    Search available properties by specified criteria.
    
    Args:
        location: Location (city or region)
        min_price: Minimum price in euros
        max_price: Maximum price in euros
        property_type: Property type (apartment, house, studio)
        
    Returns:
        JSON list of found properties
    """
    # Return mock data for demonstration purposes
    sample_properties = [
        {
            "id": "prop_001",
            "title": "Moderne 2-Zimmer-Wohnung in München",
            "location": "München, Bayern", 
            "price": 285000,
            "size_sqm": 65,
            "rooms": 2,
            "energy_class": "A+",
            "completion_year": 2024,
            "rental_guarantee": True,
            "warranty_years": 5,
            "description": "Neubau-Eigentumswohnung mit höchstem Energiestandard A+, zentral gelegen mit U-Bahn-Anschluss. Erstvermietungsgarantie für 12 Monate.",
            "monthly_investment": 180,
            "expected_rental_income": 1200
        },
        {
            "id": "prop_002", 
            "title": "3-Zimmer-Wohnung in Berlin-Spandau",
            "location": "Berlin, Berlin",
            "price": 320000,
            "size_sqm": 85,
            "rooms": 3,
            "energy_class": "A+",
            "completion_year": 2024,
            "rental_guarantee": True,
            "warranty_years": 5,
            "description": "Familienfreundliche Neubau-Wohnung mit Balkon und Parkplatz. Energieeffiziente Bauweise für niedrige Nebenkosten.",
            "monthly_investment": 195,
            "expected_rental_income": 1450
        },
        {
            "id": "prop_003",
            "title": "1-Zimmer-Apartment in Hamburg",
            "location": "Hamburg, Hamburg",
            "price": 210000,
            "size_sqm": 42,
            "rooms": 1,
            "energy_class": "A+",
            "completion_year": 2024,
            "rental_guarantee": True,
            "warranty_years": 5,
            "description": "Kompakte Single-Wohnung in begehrter Lage. Ideal für Kapitalanleger mit geringem Eigenkapitaleinsatz.",
            "monthly_investment": 145,
            "expected_rental_income": 850
        }
    ]
    
    # Filter properties by criteria
    filtered_properties = sample_properties
    
    if location:
        filtered_properties = [p for p in filtered_properties if location.lower() in p["location"].lower()]
    
    if min_price:
        filtered_properties = [p for p in filtered_properties if p["price"] >= min_price]
        
    if max_price:
        filtered_properties = [p for p in filtered_properties if p["price"] <= max_price]
    
    return json.dumps(filtered_properties, ensure_ascii=False, indent=2)


@FunctionTool 
def get_property_details(property_id: str) -> str:
    """
    Get detailed information about a property.
    
    Args:
        property_id: Property ID
        
    Returns:
        Detailed property information in JSON format
    """
    # Mock data for demonstration
    property_details = {
        "prop_001": {
            "id": "prop_001",
            "title": "Moderne 2-Zimmer-Wohnung in München",
            "location": {
                "city": "München",
                "district": "Schwabing-West", 
                "state": "Bayern",
                "postal_code": "80809",
                "address": "Leopoldstraße 125"
            },
            "financial_details": {
                "purchase_price": 285000,
                "notary_costs": 2850,
                "property_tax": 8550,
                "total_acquisition_cost": 296400,
                "down_payment_min": 15000,
                "monthly_loan_payment": 950,
                "monthly_rental_income": 1200,
                "monthly_net_income": 180,
                "roi_annual": 5.2,
                "tax_depreciation": 14250  # 5% special depreciation
            },
            "property_specs": {
                "size_sqm": 65,
                "rooms": 2,
                "bathrooms": 1,
                "floor": 3,
                "balcony": True,
                "elevator": True,
                "parking": False,
                "energy_class": "A+",
                "heating_type": "Fernwärme",
                "construction_year": 2024
            },
            "investment_benefits": {
                "rental_guarantee_months": 12,
                "warranty_years": 5,
                "energy_efficiency_grant": True,
                "capital_recovery_years": 4,
                "monthly_investment_avg": 180,
                "tax_return_potential": 15000
            },
            "developer": {
                "name": "Bauwerk München GmbH",
                "rating": "A+",
                "experience_years": 25,
                "completed_projects": 150
            }
        }
    }
    
    if property_id in property_details:
        return json.dumps(property_details[property_id], ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "Objekt nicht gefunden"}, ensure_ascii=False)


@FunctionTool
def calculate_investment_return(
    purchase_price: int,
    down_payment: int,
    monthly_rental_income: int,
    monthly_costs: int = 200,
    loan_interest_rate: float = 3.5,
    loan_term_years: int = 30,
    user_tax_rate: float = 0.42
) -> str:
    """
    Calculate investment return for real estate investment.
    
    Args:
        purchase_price: Purchase price in euros
        down_payment: Down payment in euros
        monthly_rental_income: Monthly rental income in euros
        monthly_costs: Monthly costs in euros (default 200)
        loan_interest_rate: Loan interest rate (default 3.5%)
        loan_term_years: Loan term in years (default 30)
        user_tax_rate: User tax rate (default 42%)
        
    Returns:
        Detailed return calculation in JSON format
    """
    # Basic calculations
    loan_amount = purchase_price - down_payment
    monthly_interest_rate = loan_interest_rate / 100 / 12
    num_payments = loan_term_years * 12
    
    # Calculate monthly loan payment
    if monthly_interest_rate > 0:
        monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**num_payments) / ((1 + monthly_interest_rate)**num_payments - 1)
    else:
        monthly_payment = loan_amount / num_payments
        
    # Monthly profit/loss
    monthly_net_income = monthly_rental_income - monthly_payment - monthly_costs
    
    # Tax benefits (5% special depreciation for new buildings)
    annual_depreciation = purchase_price * 0.05  # 5% per year
    annual_tax_savings = annual_depreciation * user_tax_rate
    monthly_tax_savings = annual_tax_savings / 12
    
    # Including tax benefits
    monthly_net_with_tax = monthly_net_income + monthly_tax_savings
    
    # Capital recovery after 4 years (through tax benefits)
    capital_recovery_4_years = annual_tax_savings * 4
    
    # Long-term calculations
    total_paid_10_years = (monthly_payment + monthly_costs) * 120
    total_rental_10_years = monthly_rental_income * 120
    total_tax_savings_10_years = annual_tax_savings * 10
    
    net_profit_10_years = total_rental_10_years + total_tax_savings_10_years - total_paid_10_years
    
    calculation_result = {
        "input_parameters": {
            "purchase_price": purchase_price,
            "down_payment": down_payment,
            "loan_amount": loan_amount,
            "monthly_rental_income": monthly_rental_income,
            "monthly_costs": monthly_costs,
            "loan_interest_rate": loan_interest_rate,
            "loan_term_years": loan_term_years,
            "user_tax_rate": user_tax_rate
        },
        "monthly_calculations": {
            "monthly_loan_payment": round(monthly_payment, 2),
            "monthly_rental_income": monthly_rental_income,
            "monthly_costs": monthly_costs,
            "monthly_net_before_tax": round(monthly_net_income, 2),
            "monthly_tax_savings": round(monthly_tax_savings, 2),
            "monthly_net_with_tax": round(monthly_net_with_tax, 2)
        },
        "annual_benefits": {
            "annual_depreciation": round(annual_depreciation, 2),
            "annual_tax_savings": round(annual_tax_savings, 2),
            "annual_net_income": round(monthly_net_with_tax * 12, 2)
        },
        "long_term_projections": {
            "capital_recovery_4_years": round(capital_recovery_4_years, 2),
            "net_profit_10_years": round(net_profit_10_years, 2),
            "roi_annual_percent": round((monthly_net_with_tax * 12 / down_payment) * 100, 2),
            "payback_period_years": round(down_payment / (monthly_net_with_tax * 12), 1) if monthly_net_with_tax > 0 else "Nicht rentabel"
        },
        "summary": {
            "recommended": monthly_net_with_tax > 0,
            "risk_level": "Niedrig" if monthly_net_with_tax > 100 else "Mittel" if monthly_net_with_tax > 0 else "Hoch",
            "key_benefits": [
                "5% Sonder-AfA für Neubau",
                "Erstvermietungsgarantie",
                "Energieeffizienzklasse A+",
                "5 Jahre Gewährleistung"
            ]
        }
    }
    
    return json.dumps(calculation_result, ensure_ascii=False, indent=2) 