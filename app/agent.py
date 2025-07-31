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
ImmoAssist Multi-Agent System for German Real Estate Investment Consulting.

Enterprise-ready multi-agent system following ADK best practices with:
- Modular, focused prompts (50% reduction from original monolithic versions)
- Consistent base security and communication rules across all agents
- Role-specific expertise without redundancy
- Production-ready observability and health monitoring
"""

import logging
from typing import List, Optional

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

# Import observability for monitoring
from .observability import monitor_agent, track_user_interaction, track_error, AlertSeverity

from .config import config
# Import focused, modular prompts following ADK best practices
from .prompts import (
    KNOWLEDGE_SPECIALIST_PROMPT,
    PROPERTY_SPECIALIST_PROMPT,
    CALCULATOR_SPECIALIST_PROMPT,
    MARKET_ANALYST_PROMPT,
    ROOT_AGENT_PROMPT,
    LEGAL_SPECIALIST_PROMPT,
    COORDINATION_SPECIALIST_PROMPT,
    PRESENTATION_SPECIALIST_PROMPT,
)
from .tools.integration_tools import (
    generate_audio_elevenlabs,
    send_email
)
from .tools.knowledge_tools import search_knowledge_base
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
from .tools.legal_tools import search_legal_rag
from .tools.presentation_tools import search_presentation_rag
from .tools.chart_tools import create_chart
from .tools.datetime_tools import get_current_berlin_time
from .shared_libraries.combined_callbacks import (
    enhanced_before_agent_callback,
    after_agent_conversation_callback,
)

logger = logging.getLogger(__name__)

# ===== AGENT INITIALIZATION =====
# All agents now use focused, modular prompts following ADK best practices
# Each prompt combines base_system_prompt + role-specific instructions
# Prompts are ~50% shorter and focused on single responsibilities

# Initialize Knowledge Specialist Agent for general information and definitions
knowledge_specialist = Agent(
    model=config.specialist_model,
    name="KnowledgeSpecialist",
    instruction=KNOWLEDGE_SPECIALIST_PROMPT,
    tools=[search_knowledge_base, get_current_berlin_time],
)

# Initialize Property Specialist Agent for property search and analysis
property_specialist = Agent(
    model=config.specialist_model,
    name="PropertySpecialist",
    instruction=PROPERTY_SPECIALIST_PROMPT,
    tools=[
        search_properties,
        get_property_details,
        get_current_berlin_time,
    ],
)

# Initialize Calculator Specialist Agent for investment calculations
calculator_specialist = Agent(
    model=config.specialist_model,
    name="CalculatorSpecialist",
    instruction=CALCULATOR_SPECIALIST_PROMPT,
    tools=[calculate_investment_return, get_current_berlin_time],
)

# Initialize Market Analyst Agent for market trend analysis
market_analyst = Agent(
    model=config.specialist_model,
    name="MarketAnalyst",
    instruction=MARKET_ANALYST_PROMPT,
    tools=[get_current_berlin_time],  # Analysis based on provided data and current time
)

# Initialize Legal Specialist Agent for German real estate law
legal_specialist = Agent(
    model=config.specialist_model,
    name="LegalSpecialist",
    instruction=LEGAL_SPECIALIST_PROMPT,
    tools=[search_legal_rag, get_current_berlin_time],
)

# Initialize Presentation Specialist Agent for course materials
presentation_specialist = Agent(
    model=config.specialist_model,
    name="PresentationSpecialist",
    instruction=PRESENTATION_SPECIALIST_PROMPT,
    tools=[search_presentation_rag, get_current_berlin_time],
)

def _build_coordination_tools() -> List[object]:
    """Build coordination specialist tools based on enabled feature flags.
    
    Returns:
        List of available tools for the coordination specialist agent.
    """
    tools = [
        analyze_conversation_context,
        memorize_conversation,
        recall_conversation,
        get_current_berlin_time,
    ]
    
    # Add integration tools based on feature flag configuration
    if config.get_feature_flag("enable_voice_synthesis"):
        tools.append(generate_audio_elevenlabs)
    
    if config.get_feature_flag("enable_email_notifications"):
        tools.append(send_email)
    
    return tools

# Initialize Coordination Specialist Agent for multi-domain analysis
coordination_specialist = Agent(
    model=config.chat_model,
    name="CoordinationSpecialist",
    instruction=COORDINATION_SPECIALIST_PROMPT,
    tools=_build_coordination_tools(),
    before_agent_callback=enhanced_before_agent_callback,
    after_agent_callback=after_agent_conversation_callback,
)

# Initialize Root Agent as main orchestrator with specialized sub-agents
root_agent = Agent(
    model=config.main_agent_model,
    name="ImmoAssistInvestmentAdvisor",
    instruction=ROOT_AGENT_PROMPT,
    before_agent_callback=enhanced_before_agent_callback,
    after_agent_callback=after_agent_conversation_callback,
    tools=[
        AgentTool(agent=knowledge_specialist),
        AgentTool(agent=property_specialist),
        AgentTool(agent=calculator_specialist),
        AgentTool(agent=market_analyst),
        AgentTool(agent=legal_specialist),
        AgentTool(agent=presentation_specialist),
        AgentTool(agent=coordination_specialist),
        create_chart,  # Chart generation functionality
        get_current_berlin_time,  # Current Berlin time utility
        recall_conversation,  # Enhanced conversation memory access
    ],
)

# Note: initialize_conversation_memory_callback is used as a callback function
# and should not be called directly in agent initialization
