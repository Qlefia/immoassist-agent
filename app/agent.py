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

"""ImmoAssist Multi-Agent System for German Real Estate Investment Consulting."""

import logging
from typing import List

from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .config import config
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
from .shared_libraries.conversation_callbacks import (
    combined_before_agent_callback,
    after_agent_conversation_callback,
)

logger = logging.getLogger(__name__)

# Knowledge Specialist Agent
knowledge_specialist = Agent(
    model=config.specialist_model,
    name="KnowledgeSpecialist",
    instruction=KNOWLEDGE_SPECIALIST_PROMPT,
    tools=[search_knowledge_base],
)

# Property Specialist Agent  
property_specialist = Agent(
    model=config.specialist_model,
    name="PropertySpecialist",
    instruction=PROPERTY_SPECIALIST_PROMPT,
    tools=[
        search_properties,
        get_property_details,
    ],
)

# Calculator Specialist Agent
calculator_specialist = Agent(
    model=config.specialist_model,
    name="CalculatorSpecialist",
    instruction=CALCULATOR_SPECIALIST_PROMPT,
    tools=[calculate_investment_return],
)

# Market Analyst Agent
market_analyst = Agent(
    model=config.specialist_model,
    name="MarketAnalyst",
    instruction=MARKET_ANALYST_PROMPT,
    tools=[],  # Analysis based on provided data
)

# Legal Specialist Agent
legal_specialist = Agent(
    model=config.specialist_model,
    name="LegalSpecialist",
    instruction=LEGAL_SPECIALIST_PROMPT,
    tools=[search_legal_rag],
)

# Presentation Specialist Agent
presentation_specialist = Agent(
    model=config.specialist_model,
    name="PresentationSpecialist",
    instruction=PRESENTATION_SPECIALIST_PROMPT,
    tools=[search_presentation_rag],
)

# Build Coordination Specialist tools dynamically
def _build_coordination_tools() -> List:
    """Build coordination specialist tools based on enabled features."""
    tools = [
        analyze_conversation_context,
        memorize_conversation,
        recall_conversation,
    ]
    
    # Add integration tools if features are enabled
    if config.get_feature_flag("enable_voice_synthesis"):
        tools.append(generate_audio_elevenlabs)
    
    if config.get_feature_flag("enable_email_notifications"):
        tools.append(send_email)
    
    return tools

# Coordination Specialist Agent
coordination_specialist = Agent(
    model=config.chat_model,
    name="CoordinationSpecialist",
    instruction=COORDINATION_SPECIALIST_PROMPT,
    tools=_build_coordination_tools(),
    before_agent_callback=combined_before_agent_callback,
    after_agent_callback=after_agent_conversation_callback,
)

# Main Router Agent with sub-agents
root_agent = Agent(
    model=config.main_agent_model,
    name="ImmoAssistInvestmentAdvisor",
    instruction=ROOT_AGENT_PROMPT,
    before_agent_callback=combined_before_agent_callback,
    after_agent_callback=after_agent_conversation_callback,
    tools=[
        AgentTool(agent=knowledge_specialist),
        AgentTool(agent=property_specialist),
        AgentTool(agent=calculator_specialist),
        AgentTool(agent=market_analyst),
        AgentTool(agent=legal_specialist),
        AgentTool(agent=presentation_specialist),
        AgentTool(agent=coordination_specialist),
        create_chart,  # Добавляем функцию построения графиков
    ],
)

# Note: initialize_conversation_memory_callback is used as a callback function
# and should not be called directly here
