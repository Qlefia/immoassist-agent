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
    key: str, value: str, category: str, tool_context: ToolContext
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
            "message": f"Stored {category}: '{key}' = '{value}'",
        }

    except Exception as e:
        logger.error(f"Error memorizing conversation data: {e}")
        return {"status": "error", "message": f"Memory storage error: {str(e)}"}


@FunctionTool
def recall_conversation(
    category: str, tool_context: ToolContext, specific_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves stored conversation information: discussion history, user preferences,
    and previous decisions using structured memory access.

    Args:
        category: Information category to retrieve (all, user_preferences, topics_discussed, conversation_summary, interaction_stats)
        tool_context: ADK context with access to state
        specific_key: Specific key to search for (optional)
    Returns:
        Retrieved memory information with status
    """
    try:
        state = tool_context.state
        logger.debug(f"RECALL_CONVERSATION: Checking state for memory data")

        # Check if conversation is initialized OR message history exists (fallback)
        has_init_flag = const.CONVERSATION_INITIALIZED in state
        message_history = state.get("message_history", [])
        has_messages = len(message_history) > 0

        logger.debug(
            f"RECALL_CONVERSATION: has_init_flag={has_init_flag}, has_messages={has_messages}, total_messages={len(message_history)}"
        )

        if not has_init_flag and not has_messages:
            return {
                "status": "empty",
                "message": "Conversation just started, memory is empty.",
            }

        if category == "all":
            message_history = state.get("message_history", [])
            return {
                "status": "success",
                "data": {
                    "user_preferences": state.get(const.USER_PREFERENCES, {}),
                    "topics_discussed": state.get(const.TOPICS_DISCUSSED, []),
                    "conversation_phase": state.get(
                        const.CONVERSATION_PHASE, const.PHASE_OPENING
                    ),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "interaction_count": state.get(const.INTERACTION_COUNT, 0),
                    "message_history": message_history,
                    "total_messages": len(message_history),
                },
            }

        elif category == "user_preferences":
            preferences = state.get(const.USER_PREFERENCES, {})
            if specific_key:
                value = preferences.get(specific_key)
                return {
                    "status": "success",
                    "data": {specific_key: value} if value else {},
                    "message": (
                        f"Preference '{specific_key}': {value}"
                        if value
                        else f"Preference '{specific_key}' not found"
                    ),
                }
            return {
                "status": "success",
                "data": preferences,
                "message": f"Found {len(preferences)} user preferences",
            }

        elif category == "topics_discussed":
            topics = state.get(const.TOPICS_DISCUSSED, [])
            return {
                "status": "success",
                "data": topics,
                "message": f"Discussion topics: {', '.join(topics) if topics else 'no topics discussed yet'}",
            }

        elif category == "conversation_summary":
            return {
                "status": "success",
                "data": {
                    "phase": state.get(const.CONVERSATION_PHASE, const.PHASE_OPENING),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "topics_count": len(state.get(const.TOPICS_DISCUSSED, [])),
                    "last_interaction": state.get(const.LAST_INTERACTION_TYPE, "none"),
                    "session_duration": _calculate_session_duration(state),
                },
            }

        elif category == "message_history":
            message_history = state.get("message_history", [])
            if specific_key:
                try:
                    message_number = int(specific_key)
                    if 1 <= message_number <= len(message_history):
                        message = message_history[
                            message_number - 1
                        ]  # Convert to 0-based index
                        return {
                            "status": "success",
                            "data": message,
                            "message": f"Message #{message_number}: {message.get('user_input', 'No text')}",
                        }
                    else:
                        return {
                            "status": "not_found",
                            "message": f"Message #{message_number} not found. Available: 1-{len(message_history)}",
                        }
                except ValueError:
                    return {
                        "status": "error",
                        "message": f"Invalid message number: {specific_key}",
                    }
            return {
                "status": "success",
                "data": message_history,
                "message": f"Found {len(message_history)} messages in history",
            }

        elif category == "interaction_stats":
            return {
                "status": "success",
                "data": {
                    "total_interactions": state.get(const.INTERACTION_COUNT, 0),
                    "greeting_count": state.get(const.GREETING_COUNT, 0),
                    "conversation_phase": state.get(
                        const.CONVERSATION_PHASE, const.PHASE_OPENING
                    ),
                    "language": state.get(const.LANGUAGE_PREFERENCE, "unknown"),
                    "communication_style": state.get(
                        const.COMMUNICATION_STYLE, "unknown"
                    ),
                },
            }

        elif category == "message_history":
            message_history = state.get("message_history", [])
            if specific_key:
                # Try to find message by number (e.g., "2" for second message)
                try:
                    message_num = int(specific_key)
                    if 1 <= message_num <= len(message_history):
                        message = message_history[message_num - 1]
                        return {
                            "status": "success",
                            "data": message,
                            "message": f"Message #{message_num}: '{message['user_input']}'",
                        }
                    else:
                        return {
                            "status": "error",
                            "message": f"Message #{message_num} not found. Available: 1-{len(message_history)}",
                        }
                except ValueError:
                    # Search by content
                    matching_messages = []
                    for msg in message_history:
                        if specific_key.lower() in msg["user_input"].lower():
                            matching_messages.append(msg)
                    return {
                        "status": "success",
                        "data": matching_messages,
                        "message": f"Found {len(matching_messages)} messages containing '{specific_key}'",
                    }
            else:
                return {
                    "status": "success",
                    "data": message_history,
                    "message": f"All {len(message_history)} messages retrieved",
                }

        return {"status": "error", "message": f"Unknown category: {category}"}

    except Exception as e:
        logger.error(f"Error recalling conversation data: {e}")
        return {"status": "error", "message": f"Memory retrieval error: {str(e)}"}


# --- Removed duplicate functions - use recall_conversation directly ---


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


@FunctionTool
def get_user_preferences(
    tool_context: ToolContext, preference_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves user preferences from memory.

    Args:
        tool_context: ADK context with access to state
        preference_key: Specific preference to retrieve (optional)

    Returns:
        User preferences data
    """
    try:
        state = tool_context.state
        preferences = state.get(const.USER_PREFERENCES, {})

        if preference_key:
            # Look for the key in all preference categories
            for category, category_prefs in preferences.items():
                if (
                    isinstance(category_prefs, dict)
                    and preference_key in category_prefs
                ):
                    return {
                        "status": "success",
                        "data": {preference_key: category_prefs[preference_key]},
                        "message": f"Found preference '{preference_key}' in category '{category}'",
                    }

            return {
                "status": "not_found",
                "data": {},
                "message": f"Preference '{preference_key}' not found",
            }
        else:
            return {
                "status": "success",
                "data": preferences,
                "message": f"Retrieved all user preferences",
            }

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return {"status": "error", "message": f"Error retrieving preferences: {str(e)}"}


@FunctionTool
def update_user_preferences(
    preference_key: str,
    preference_value: str,
    tool_context: ToolContext,
    category: str = "user_preference",
) -> Dict[str, Any]:
    """
    Updates user preferences in memory.

    Args:
        preference_key: Key for the preference
        preference_value: Value to store
        tool_context: ADK context with access to state
        category: Preference category (default: user_preference)

    Returns:
        Operation status
    """
    try:
        state = tool_context.state

        # Initialize preferences if not exists
        if const.USER_PREFERENCES not in state:
            state[const.USER_PREFERENCES] = {}

        if category not in state[const.USER_PREFERENCES]:
            state[const.USER_PREFERENCES][category] = {}

        state[const.USER_PREFERENCES][category][preference_key] = preference_value

        logger.info(
            f"Updated user preference: {preference_key} = {preference_value} (category: {category})"
        )

        return {
            "status": "success",
            "message": f"Updated preference '{preference_key}' in category '{category}'",
        }

    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        return {"status": "error", "message": f"Error updating preferences: {str(e)}"}
