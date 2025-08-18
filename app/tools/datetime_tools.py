"""
Datetime tools for ImmoAssist - provides current Berlin time and date.

Essential for ensuring all agents work with accurate, up-to-date information
including current market data, legal changes, and time-sensitive calculations.
"""

from datetime import datetime
import pytz
from typing import Dict, Any
from google.adk.tools import FunctionTool


@FunctionTool
def get_current_berlin_time() -> Dict[str, Any]:
    """
    Get current date and time in Berlin timezone.
    
    This function ensures all ImmoAssist agents work with accurate,
    up-to-date temporal information for:
    - Market analysis and trends
    - Legal and regulatory changes
    - Time-sensitive investment calculations
    - Current property market conditions
    
    Returns:
        Dict containing current Berlin date/time information
        
    Example:
        {
            "current_date": "2024-12-19",
            "current_time": "14:30:25",
            "current_datetime": "2024-12-19 14:30:25",
            "timezone": "Europe/Berlin",
            "day_of_week": "Thursday",
            "formatted_date": "19. Dezember 2024"
        }
    """
    # Get Berlin timezone
    berlin_tz = pytz.timezone('Europe/Berlin')
    
    # Get current time in Berlin
    now_berlin = datetime.now(berlin_tz)
    
    # German day names
    german_days = {
        0: "Montag", 1: "Dienstag", 2: "Mittwoch", 
        3: "Donnerstag", 4: "Freitag", 5: "Samstag", 6: "Sonntag"
    }
    
    # German month names
    german_months = {
        1: "Januar", 2: "Februar", 3: "März", 4: "April",
        5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
        9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
    }
    
    return {
        "current_date": now_berlin.strftime("%Y-%m-%d"),
        "current_time": now_berlin.strftime("%H:%M:%S"),
        "current_datetime": now_berlin.strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": "Europe/Berlin (CET/CEST)",
        "day_of_week": german_days[now_berlin.weekday()],
        "month_name": german_months[now_berlin.month],
        "formatted_date": f"{now_berlin.day}. {german_months[now_berlin.month]} {now_berlin.year}",
        "year": now_berlin.year,
        "month": now_berlin.month,
        "day": now_berlin.day,
        "hour": now_berlin.hour,
        "minute": now_berlin.minute,
        "iso_format": now_berlin.isoformat(),
        "timestamp": int(now_berlin.timestamp())
    } 