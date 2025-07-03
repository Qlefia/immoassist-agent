"""
Tools and utilities for ImmoAssist AI Agent.

This module provides all the tools used by the ImmoAssist agent,
including property search, user management, knowledge base, and integration tools.
"""

from .property_tools import (
    search_properties,
    get_property_details,
    calculate_investment_return
)

from .user_tools import (
    get_user_profile,
    save_user_calculation,
    get_user_history,
    log_user_interaction,
    update_user_preferences
)

from .knowledge_tools import (
    search_faq,
    search_handbook,
    get_knowledge_categories,
    add_knowledge_entry
)

from .integration_tools import (
    send_heygen_avatar_message,
    generate_elevenlabs_audio,
    create_appointment_link,
    send_email_notification,
    generate_3d_property_visualization
)

__all__ = [
    "search_properties",
    "get_property_details", 
    "calculate_investment_return",
    "get_user_profile",
    "save_user_calculation",
    "get_user_history",
    "log_user_interaction",
    "update_user_preferences",
    "search_faq",
    "search_handbook",
    "get_knowledge_categories",
    "add_knowledge_entry",
    "send_heygen_avatar_message",
    "generate_elevenlabs_audio",
    "create_appointment_link",
    "send_email_notification",
    "generate_3d_property_visualization"
] 