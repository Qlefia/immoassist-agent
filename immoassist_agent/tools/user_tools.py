"""
User management tools for ImmoAssist.

This module contains tools for managing user profiles, saving calculations,
tracking user history, and maintaining user preferences and interactions.
"""

from typing import Dict, List, Optional
from google.adk.tools import FunctionTool
import json
from datetime import datetime

# Temporary user data storage (will be replaced with database in production)
USER_DATA_STORE = {}
USER_CALCULATIONS_STORE = {}
USER_HISTORY_STORE = {}

@FunctionTool
def get_user_profile(user_id: str) -> str:
    """
    Get user profile with preferences and data.
    
    Args:
        user_id: User ID
        
    Returns:
        User profile in JSON format
    """
    # Mock data for demonstration
    if user_id not in USER_DATA_STORE:
        # Create new user profile
        USER_DATA_STORE[user_id] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "preferences": {
                "language": "de",
                "preferred_locations": [],
                "budget_min": None,
                "budget_max": None,
                "risk_tolerance": "moderate",  # conservative, moderate, aggressive
                "investment_goals": [],
                "communication_preference": "chat"  # chat, email, phone
            },
            "financial_profile": {
                "monthly_income": None,
                "available_capital": None,
                "tax_rate": 0.42,
                "existing_properties": 0,
                "credit_score": None
            },
            "contact_info": {
                "email": None,
                "phone": None,
                "name": None
            },
            "consultation_status": {
                "step": 1,  # Current consultation stage (1-6)
                "completed_steps": [],
                "next_appointment": None
            }
        }
    
    return json.dumps(USER_DATA_STORE[user_id], ensure_ascii=False, indent=2)


@FunctionTool
def save_user_calculation(
    user_id: str,
    calculation_type: str,
    calculation_data: str,
    property_id: Optional[str] = None
) -> str:
    """
    Save user calculation for long-term memory.
    
    Args:
        user_id: User ID
        calculation_type: Calculation type (investment_return, affordability, etc.)
        calculation_data: Calculation data in JSON format
        property_id: Property ID (if applicable)
        
    Returns:
        Save confirmation
    """
    if user_id not in USER_CALCULATIONS_STORE:
        USER_CALCULATIONS_STORE[user_id] = []
    
    calculation_record = {
        "id": f"calc_{len(USER_CALCULATIONS_STORE[user_id]) + 1}",
        "user_id": user_id,
        "calculation_type": calculation_type,
        "calculation_data": json.loads(calculation_data) if isinstance(calculation_data, str) else calculation_data,
        "property_id": property_id,
        "created_at": datetime.now().isoformat()
    }
    
    USER_CALCULATIONS_STORE[user_id].append(calculation_record)
    
    return json.dumps({
        "status": "success",
        "message": f"Calculation saved for user {user_id}",
        "calculation_id": calculation_record["id"]
    }, ensure_ascii=False)


@FunctionTool
def get_user_history(user_id: str, limit: int = 10) -> str:
    """
    Get user interaction history.
    
    Args:
        user_id: User ID
        limit: Maximum number of records
        
    Returns:
        Interaction history in JSON format
    """
    if user_id not in USER_HISTORY_STORE:
        USER_HISTORY_STORE[user_id] = []
    
    # Get recent records
    history = USER_HISTORY_STORE[user_id][-limit:] if USER_HISTORY_STORE[user_id] else []
    
    # Add calculations if available
    calculations = USER_CALCULATIONS_STORE.get(user_id, [])
    
    user_history = {
        "user_id": user_id,
        "total_interactions": len(USER_HISTORY_STORE.get(user_id, [])),
        "total_calculations": len(calculations),
        "recent_interactions": history,
        "saved_calculations": calculations[-5:] if calculations else [],  # Last 5 calculations
        "preferences": USER_DATA_STORE.get(user_id, {}).get("preferences", {}),
        "consultation_progress": USER_DATA_STORE.get(user_id, {}).get("consultation_status", {})
    }
    
    return json.dumps(user_history, ensure_ascii=False, indent=2)


@FunctionTool
def update_user_preferences(
    user_id: str,
    preferences_data: str
) -> str:
    """
    Update user preferences.
    
    Args:
        user_id: User ID
        preferences_data: New preferences in JSON format
        
    Returns:
        Update confirmation
    """
    if user_id not in USER_DATA_STORE:
        get_user_profile(user_id)  # Create profile if not exists
    
    try:
        new_preferences = json.loads(preferences_data) if isinstance(preferences_data, str) else preferences_data
        USER_DATA_STORE[user_id]["preferences"].update(new_preferences)
        USER_DATA_STORE[user_id]["updated_at"] = datetime.now().isoformat()
        
        return json.dumps({
            "status": "success", 
            "message": "User preferences updated",
            "updated_preferences": USER_DATA_STORE[user_id]["preferences"]
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error updating preferences: {str(e)}"
        }, ensure_ascii=False)


@FunctionTool
def log_user_interaction(
    user_id: str,
    interaction_type: str,
    interaction_data: str
) -> str:
    """
    Log user interaction to long-term memory.
    
    Args:
        user_id: User ID
        interaction_type: Interaction type (message, calculation, property_view, etc.)
        interaction_data: Interaction data
        
    Returns:
        Log confirmation
    """
    if user_id not in USER_HISTORY_STORE:
        USER_HISTORY_STORE[user_id] = []
    
    interaction_record = {
        "id": f"int_{len(USER_HISTORY_STORE[user_id]) + 1}",
        "user_id": user_id,
        "interaction_type": interaction_type,
        "interaction_data": interaction_data,
        "timestamp": datetime.now().isoformat()
    }
    
    USER_HISTORY_STORE[user_id].append(interaction_record)
    
    # Limit number of records in memory
    if len(USER_HISTORY_STORE[user_id]) > 100:
        USER_HISTORY_STORE[user_id] = USER_HISTORY_STORE[user_id][-100:]
    
    return json.dumps({
        "status": "success",
        "message": "Interaction logged"
    }, ensure_ascii=False) 