"""
Memory Management Tools for ImmoAssist.

Tools for conversation memory management using callback_context.state
as the primary storage, following ADK agent patterns.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from google.adk.tools import FunctionTool, ToolContext
from google.adk.agents.callback_context import CallbackContext

from ..shared_libraries import conversation_constants as const

logger = logging.getLogger(__name__)


@FunctionTool
def memorize_conversation(
    key: str, 
    value: str, 
    category: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    Stores important conversation information: user preferences, discussed topics,
    decisions, and context for future interactions using structured memory categories.
    
    Args:
        key: Storage key for the information (e.g., user_budget, preferred_location, discussed_yield)
        value: Value to be stored
        category: Information category (user_preference, topic_discussed, decision_made, context_note)
        tool_context: ADK context with access to state
        
    Returns:
        Operation status and confirmation message
    """
    try:
        state = tool_context.state
        if const.USER_PREFERENCES not in state:
            state[const.USER_PREFERENCES] = {}

        # Ensure category dictionary exists
        if category not in state[const.USER_PREFERENCES]:
            state[const.USER_PREFERENCES][category] = {}
            
        state[const.USER_PREFERENCES][category][key] = value
        
        logger.info(f"Memorized '{key}' in category '{category}'")
        
        return {
            "status": "success",
            "message": f"Stored {category}: '{key}' = '{value}'"
        }
        
    except Exception as e:
        logger.error(f"Error memorizing conversation data: {e}")
        return {
            "status": "error", 
            "message": f"Memory storage error: {str(e)}"
        }


@FunctionTool
def recall_conversation(
    category: str, 
    specific_key: Optional[str] = None,
    tool_context: ToolContext = None,
    session_context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Retrieves stored conversation information: discussion history, user preferences,
    and previous decisions using structured memory access.
    
    Args:
        category: Information category to retrieve (all, user_preferences, topics_discussed, conversation_summary, interaction_stats)
        specific_key: Specific key to search for (optional)
        tool_context: ADK context with access to state
        session_context: Alternative context dict (for compatibility)
    Returns:
        Retrieved memory information with status
    """
    try:
        if tool_context is not None:
            state = tool_context.state
        elif session_context is not None:
            state = session_context
        else:
            return {
                "status": "error",
                "message": "No context provided for recall_conversation"
            }
        
        if const.CONVERSATION_INITIALIZED not in state:
            return {
                "status": "empty",
                "message": "Conversation just started, memory is empty.",
                "data": {}
            }
        
        if category == "all":
            return {
                "status": "success",
                "data": {
                    "user_preferences": state.get(const.USER_PREFERENCES, {}),
                    "topics_discussed": state.get(const.TOPICS_DISCUSSED, []),
                    "conversation_phase": state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "interaction_count": state.get(const.INTERACTION_COUNT, 0)
                }
            }
        
        elif category == "user_preferences":
            preferences = state.get(const.USER_PREFERENCES, {})
            if specific_key:
                value = preferences.get(specific_key)
                return {
                    "status": "success",
                    "data": {specific_key: value} if value else {},
                    "message": f"Preference '{specific_key}': {value}" if value else f"Preference '{specific_key}' not found"
                }
            return {
                "status": "success", 
                "data": preferences,
                "message": f"Found {len(preferences)} user preferences"
            }
        
        elif category == "topics_discussed":
            topics = state.get(const.TOPICS_DISCUSSED, [])
            return {
                "status": "success",
                "data": topics,
                "message": f"Discussion topics: {', '.join(topics) if topics else 'no topics discussed yet'}"
            }
        
        elif category == "conversation_summary":
            return {
                "status": "success",
                "data": {
                    "phase": state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "topics_count": len(state.get(const.TOPICS_DISCUSSED, [])),
                    "last_interaction": state.get(const.LAST_INTERACTION_TYPE, "none"),
                    "session_duration": _calculate_session_duration(state)
                }
            }
        
        elif category == "interaction_stats":
            return {
                "status": "success",
                "data": {
                    "total_interactions": state.get(const.INTERACTION_COUNT, 0),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "conversation_phase": state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING),
                    "language": state.get(const.LANGUAGE_PREFERENCE, "unknown"),
                    "communication_style": state.get(const.COMMUNICATION_STYLE, "unknown")
                }
            }
        
        return {
            "status": "error",
            "message": f"Unknown category: {category}"
        }
        
    except Exception as e:
        logger.error(f"Error recalling conversation data: {e}")
        return {
            "status": "error",
            "message": f"Memory retrieval error: {str(e)}"
        }


def _initialize_conversation_state(state: Dict[str, Any]) -> None:
    """Initializes conversation state in ADK state storage."""
    if const.CONVERSATION_INITIALIZED not in state:
        state[const.CONVERSATION_INITIALIZED] = True
        state[const.SESSION_START_TIME] = datetime.now().isoformat()
        state[const.GREETING_COUNT] = 0
        state[const.INTERACTION_COUNT] = 0
        state[const.CONVERSATION_PHASE] = const.PHASE_OPENING
        state[const.TOPICS_DISCUSSED] = []
        state[const.USER_PREFERENCES] = {}
        state[const.LAST_INTERACTION_TYPE] = const.INTERACTION_GREETING
        
        logger.info("Initialized conversation state")


def _calculate_session_duration(state: Dict[str, Any]) -> str:
    """Calculates session duration from start time."""
    try:
        start_time_str = state.get(const.SESSION_START_TIME)
        if not start_time_str:
            return "unknown"
            
        start_time = datetime.fromisoformat(start_time_str)
        duration = datetime.now() - start_time
        
        total_minutes = int(duration.total_seconds() / 60)
        
        if total_minutes < 1:
            return "less than 1 minute"
        elif total_minutes < 60:
            return f"{total_minutes} minutes"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            return f"{hours}h {minutes}m"
            
    except Exception as e:
        logger.error(f"Error calculating session duration: {e}")
        return "calculation error"


def initialize_conversation_memory_callback(callback_context: CallbackContext) -> None:
    """
    Callback function to initialize conversation memory in ADK state.
    Called before agent processing to ensure memory structure exists.
    
    Args:
        callback_context: ADK callback context with access to state
    """
    try:
        state = callback_context.state
        _initialize_conversation_state(state)
        logger.debug("Conversation memory initialized via callback")
            
    except Exception as e:
        logger.error(f"Error in memory initialization callback: {e}") 