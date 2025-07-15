# Copyright 2025 ImmoAssist
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
ImmoAssist Multi-Agent System

Based on Google ADK gemini-fullstack
"""

import logging

try:
    from google.adk.agents import Agent
    from google.adk.tools.agent_tool import AgentTool
except ImportError:
    # Fallback for development environment if Google ADK is not available
    print("Warning: Could not import Google ADK components. Using fallback.")

    class Agent:
        def __init__(self, **kwargs):
            pass

    class AgentTool:
        def __init__(self, **kwargs):
            pass


from .config import config
from .prompts import (
    KNOWLEDGE_SPECIALIST_PROMPT,
    PROPERTY_SPECIALIST_PROMPT,
    CALCULATOR_SPECIALIST_PROMPT,
    MARKET_ANALYST_PROMPT,
    ROOT_AGENT_PROMPT,
)
from .tools.integration_tools import (
    generate_elevenlabs_audio,
    send_heygen_avatar_message,
)
from .tools.knowledge_tools import search_knowledge_rag
from .tools.property_tools import (
    calculate_investment_return,
    get_property_details,
    search_properties,
)
from .tools.conversation_tools import analyze_conversation_context
from .tools.memory_tools import (
    memorize_conversation,
    recall_conversation,
    initialize_conversation_memory_callback
)
from .shared_libraries.conversation_callbacks import (
    combined_before_agent_callback,
    after_agent_conversation_callback,
    conversation_style_enhancer_callback,
    before_tool_conversation_callback,
)

# Configure logging for the agent module
logging.basicConfig(level=getattr(logging, config.log_level))
logger = logging.getLogger(__name__)


# === SPECIALIST AGENTS ===
# Each agent is responsible for a specific domain and has domain-specific tools

knowledge_specialist = Agent(
    model=config.specialist_model,
    name="knowledge_specialist",
    description="Expert in German real estate law, regulations, and ImmoAssist processes.",
    instruction=KNOWLEDGE_SPECIALIST_PROMPT,
    tools=[search_knowledge_rag],
)

property_specialist = Agent(
    model=config.specialist_model,
    name="property_specialist",
    description="Expert in property search, evaluation, and German real estate market analysis.",
    instruction=PROPERTY_SPECIALIST_PROMPT,
    tools=[search_properties, get_property_details],
)

calculator_specialist = Agent(
    model=config.specialist_model,
    name="calculator_specialist",
    description="Expert in financial calculations, ROI analysis, and investment optimization.",
    instruction=CALCULATOR_SPECIALIST_PROMPT,
    tools=[calculate_investment_return],
)

market_analyst = Agent(
    model=config.specialist_model,
    name="market_analyst",
    description="Expert in German real estate market trends, analytics, and investment strategy.",
    instruction=MARKET_ANALYST_PROMPT,
    tools=[],  # Market data tools can be added here
)

# === COORDINATION AGENT ===
# Main agent that coordinates specialist agents and manages client interactions

# === AGENT TOOLS (for the root agent) ===

knowledge_specialist_tool = AgentTool(agent=knowledge_specialist)

property_specialist_tool = AgentTool(agent=property_specialist)

calculator_specialist_tool = AgentTool(agent=calculator_specialist)

coordination_specialist_tools = [
    knowledge_specialist_tool,
    property_specialist_tool,
    calculator_specialist_tool,
    AgentTool(agent=market_analyst),
    analyze_conversation_context,  # Adds conversation analysis tool
    memorize_conversation,         # Adds memory management tool
    recall_conversation,           # Adds memory recall tool
]

# Add integration tools if features are enabled
if config.get_feature_flag("enable_ai_avatar"):
    coordination_specialist_tools.append(send_heygen_avatar_message)

if config.get_feature_flag("enable_voice_synthesis"):
    coordination_specialist_tools.append(generate_elevenlabs_audio)

root_agent = Agent(
    model=config.main_agent_model,
    name="Philipp_ImmoAssist",
    description="Personal AI consultant for German real estate investments with natural conversation and memory.",
    instruction=ROOT_AGENT_PROMPT,
    tools=coordination_specialist_tools,
    # Add conversation management callbacks with state-based memory
    before_agent_callback=combined_before_agent_callback,
    before_model_callback=conversation_style_enhancer_callback,
    before_tool_callback=before_tool_conversation_callback,
    after_agent_callback=after_agent_conversation_callback,
)

# === EXPORT FOR ADK WEB INTERFACE ===
# This is the main entry point for the ADK web interface
agent = root_agent  # For compatibility

__all__ = ["root_agent", "agent"]
