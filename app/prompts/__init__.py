"""
ImmoAssist Agent Prompts

This module contains all agent prompts organized by specialist role.
"""

from .knowledge_specialist import KNOWLEDGE_SPECIALIST_PROMPT
from .property_specialist import PROPERTY_SPECIALIST_PROMPT
from .calculator_specialist import CALCULATOR_SPECIALIST_PROMPT
from .market_analyst import MARKET_ANALYST_PROMPT
from .root_agent import ROOT_AGENT_PROMPT

__all__ = [
    "KNOWLEDGE_SPECIALIST_PROMPT",
    "PROPERTY_SPECIALIST_PROMPT", 
    "CALCULATOR_SPECIALIST_PROMPT",
    "MARKET_ANALYST_PROMPT",
    "ROOT_AGENT_PROMPT",
] 