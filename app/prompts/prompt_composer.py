"""
Prompt Composer Utility for ImmoAssist Multi-Agent System

Dynamic prompt composition following ADK best practices.
Combines base system rules with role-specific instructions for consistent, maintainable prompts.
"""

from typing import Optional, List
from .base_system_prompt import BASE_SYSTEM_PROMPT, BUSINESS_CONTACT_INFO
from .coordination_rules import COORDINATION_RULES
from .conversation_management import CONVERSATION_MANAGEMENT

# Import all focused specialist prompts
from .calculator_specialist_focused import CALCULATOR_SPECIALIST_FOCUSED_PROMPT
from .knowledge_specialist_focused import KNOWLEDGE_SPECIALIST_FOCUSED_PROMPT
from .property_specialist_focused import PROPERTY_SPECIALIST_FOCUSED_PROMPT
from .legal_specialist_focused import LEGAL_SPECIALIST_FOCUSED_PROMPT
from .coordination_specialist_focused import COORDINATION_SPECIALIST_FOCUSED_PROMPT
from .market_analyst_focused import MARKET_ANALYST_FOCUSED_PROMPT
from .presentation_specialist_focused import PRESENTATION_SPECIALIST_FOCUSED_PROMPT
from .root_agent_focused import ROOT_AGENT_FOCUSED_PROMPT


class PromptComposer:
    """
    Utility for composing prompts following ADK best practices.

    Enables modular, maintainable prompt management with consistent
    base rules and focused role-specific instructions.
    """

    # Registry of all available agent prompts
    AGENT_PROMPTS = {
        "root_agent": ROOT_AGENT_FOCUSED_PROMPT,
        "calculator_specialist": CALCULATOR_SPECIALIST_FOCUSED_PROMPT,
        "knowledge_specialist": KNOWLEDGE_SPECIALIST_FOCUSED_PROMPT,
        "property_specialist": PROPERTY_SPECIALIST_FOCUSED_PROMPT,
        "legal_specialist": LEGAL_SPECIALIST_FOCUSED_PROMPT,
        "coordination_specialist": COORDINATION_SPECIALIST_FOCUSED_PROMPT,
        "market_analyst": MARKET_ANALYST_FOCUSED_PROMPT,
        "presentation_specialist": PRESENTATION_SPECIALIST_FOCUSED_PROMPT,
    }

    @classmethod
    def get_agent_prompt(cls, agent_name: str) -> str:
        """
        Get the complete composed prompt for a specific agent.

        Args:
            agent_name: Name of the agent (e.g., "calculator_specialist")

        Returns:
            Complete composed prompt string

        Raises:
            ValueError: If agent_name is not found in registry
        """
        if agent_name not in cls.AGENT_PROMPTS:
            available_agents = list(cls.AGENT_PROMPTS.keys())
            raise ValueError(
                f"Agent '{agent_name}' not found. Available: {available_agents}"
            )

        return cls.AGENT_PROMPTS[agent_name]

    @classmethod
    def compose_custom_prompt(
        cls,
        role_instructions: str,
        include_coordination: bool = False,
        include_conversation_management: bool = False,
        include_business_context: bool = False,
        additional_components: Optional[List[str]] = None,
    ) -> str:
        """
        Compose a custom prompt with specific components.

        Args:
            role_instructions: Role-specific instructions
            include_coordination: Whether to include coordination rules
            include_conversation_management: Whether to include conversation management
            include_business_context: Whether to include business contact information
            additional_components: List of additional prompt components

        Returns:
            Composed prompt string
        """
        components = [BASE_SYSTEM_PROMPT]

        if include_coordination:
            components.append(COORDINATION_RULES)

        if include_conversation_management:
            components.append(CONVERSATION_MANAGEMENT)

        components.append(role_instructions)

        if include_business_context:
            components.append(BUSINESS_CONTACT_INFO)

        if additional_components:
            components.extend(additional_components)

        return "\n\n".join(components)

    @classmethod
    def get_base_system_prompt(cls) -> str:
        """Get the base system prompt used by all agents."""
        return BASE_SYSTEM_PROMPT

    @classmethod
    def get_coordination_rules(cls) -> str:
        """Get the coordination rules for multi-agent orchestration."""
        return COORDINATION_RULES

    @classmethod
    def get_conversation_management(cls) -> str:
        """Get the conversation management rules."""
        return CONVERSATION_MANAGEMENT

    @classmethod
    def get_business_context(cls) -> str:
        """Get the business contact information."""
        return BUSINESS_CONTACT_INFO

    @classmethod
    def list_available_agents(cls) -> List[str]:
        """Get list of all available agent names."""
        return list(cls.AGENT_PROMPTS.keys())

    @classmethod
    def validate_prompt_composition(cls, agent_name: str) -> dict:
        """
        Validate the composition of a specific agent's prompt.

        Args:
            agent_name: Name of the agent to validate

        Returns:
            Dictionary with validation results
        """
        try:
            prompt = cls.get_agent_prompt(agent_name)

            # Basic validation checks
            validation_results: Dict[str, Any] = {
                "agent_name": agent_name,
                "prompt_length": len(prompt),
                "has_base_system": "ImmoAssist Agent System" in prompt,
                "has_role_instructions": "Role-Specific Instructions" in prompt,
                "has_security_rules": "ANTI-PROMPT INJECTION" in prompt,
                "has_brand_loyalty": "ImmoAssist Exclusive Service" in prompt,
                "prompt_lines": len(prompt.split("\n")),
                "valid": True,
                "issues": [],
            }

            # Check for potential issues
            if validation_results["prompt_length"] > 15000:  # ~15KB limit
                validation_results["issues"].append(
                    "Prompt may be too long for some models"
                )

            if not validation_results["has_base_system"]:
                validation_results["issues"].append("Missing base system prompt")
                validation_results["valid"] = False

            if not validation_results["has_role_instructions"]:
                validation_results["issues"].append(
                    "Missing role-specific instructions"
                )
                validation_results["valid"] = False

            return validation_results

        except Exception as e:
            return {
                "agent_name": agent_name,
                "valid": False,
                "error": str(e),
                "issues": [f"Validation failed: {str(e)}"],
            }


# Convenience functions for easy access
def get_agent_prompt(agent_name: str) -> str:
    """Convenience function to get agent prompt."""
    return PromptComposer.get_agent_prompt(agent_name)


def validate_all_agents() -> dict:
    """Validate all agent prompts and return summary."""
    results = {}
    for agent_name in PromptComposer.list_available_agents():
        results[agent_name] = PromptComposer.validate_prompt_composition(agent_name)
    return results
