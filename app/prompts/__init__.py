"""
ImmoAssist Agent Prompts

This module contains all agent prompts organized by specialist role.
Now uses focused, modular prompts following ADK best practices.
"""

# Import focused prompts from new modular system
from .prompt_composer import get_agent_prompt, PromptComposer

# Create focused prompts using the composer
KNOWLEDGE_SPECIALIST_PROMPT = get_agent_prompt("knowledge_specialist")
PROPERTY_SPECIALIST_PROMPT = get_agent_prompt("property_specialist")
CALCULATOR_SPECIALIST_PROMPT = get_agent_prompt("calculator_specialist")
MARKET_ANALYST_PROMPT = get_agent_prompt("market_analyst")
ROOT_AGENT_PROMPT = get_agent_prompt("root_agent")
LEGAL_SPECIALIST_PROMPT = get_agent_prompt("legal_specialist")
COORDINATION_SPECIALIST_PROMPT = get_agent_prompt("coordination_specialist")
PRESENTATION_SPECIALIST_PROMPT = get_agent_prompt("presentation_specialist")

# Legacy support for old imports
# Maintain backward compatibility while using new focused prompts
__all__ = [
    "KNOWLEDGE_SPECIALIST_PROMPT",
    "PROPERTY_SPECIALIST_PROMPT", 
    "CALCULATOR_SPECIALIST_PROMPT",
    "MARKET_ANALYST_PROMPT",
    "ROOT_AGENT_PROMPT",
    "LEGAL_SPECIALIST_PROMPT",
    "COORDINATION_SPECIALIST_PROMPT",
    "PRESENTATION_SPECIALIST_PROMPT",
    # Export composer utilities for advanced usage
    "get_agent_prompt",
    "PromptComposer",
] 