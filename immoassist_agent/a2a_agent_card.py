"""
A2A Agent Card Implementation for ImmoAssist

This module implements the Agent2Agent (A2A) protocol agent card
for ImmoAssist multi-agent system, enabling discovery and communication
with other AI agents following Google's A2A standard.
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

@dataclass
class AgentCapabilities:
    """Agent capabilities definition for A2A protocol."""
    streaming: bool = False
    pushNotifications: bool = True
    stateTransitionHistory: bool = True
    multiModal: bool = True
    longRunningTasks: bool = True


@dataclass 
class AgentAuthentication:
    """Authentication configuration for A2A protocol."""
    schemes: List[str]
    description: Optional[str] = None


@dataclass
class AgentSkill:
    """Individual agent skill definition."""
    id: str
    name: str
    description: str
    tags: List[str]
    examples: List[str]
    inputModes: List[str] = None
    outputModes: List[str] = None
    
    def __post_init__(self):
        if self.inputModes is None:
            self.inputModes = ["text", "text/plain"]
        if self.outputModes is None:
            self.outputModes = ["text", "text/plain", "application/json"]


@dataclass
class AgentProvider:
    """Agent provider information."""
    organization: str
    url: Optional[str] = None
    contact: Optional[str] = None


@dataclass
class AgentCard:
    """Complete A2A Agent Card following Google's specification."""
    name: str
    description: str
    url: str
    version: str
    capabilities: AgentCapabilities
    authentication: AgentAuthentication
    defaultInputModes: List[str]
    defaultOutputModes: List[str]
    skills: List[AgentSkill]
    provider: Optional[AgentProvider] = None
    documentationUrl: Optional[str] = None
    
    def to_json(self) -> str:
        """Convert agent card to JSON string."""
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent card to dictionary."""
        return asdict(self)


class ImmoAssistAgentCard:
    """ImmoAssist specific A2A Agent Card generator."""
    
    @staticmethod
    def create_card(base_url: str = None) -> AgentCard:
        """Create ImmoAssist A2A Agent Card."""
        
        if base_url is None:
            host = os.getenv("ADK_HOST", "localhost")
            port = os.getenv("ADK_PORT", "8001")
            base_url = f"http://{host}:{port}"
        
        # Define capabilities
        capabilities = AgentCapabilities(
            streaming=True,
            pushNotifications=True,
            stateTransitionHistory=True,
            multiModal=True,
            longRunningTasks=True
        )
        
        # Authentication (OAuth 2.0 Bearer tokens in production)
        authentication = AgentAuthentication(
            schemes=["Bearer", "Basic"],
            description="OAuth 2.0 Bearer token or Basic authentication for development"
        )
        
        # Define agent skills
        skills = [
            AgentSkill(
                id="real_estate_consultation",
                name="German Real Estate Investment Consultation",
                description="Comprehensive consultation for German new-construction real estate investments (250k-500k EUR)",
                tags=["real estate", "investment", "germany", "consultation", "neubau"],
                examples=[
                    "Ich möchte in eine Neubau-Immobilie in München investieren",
                    "Wie hoch ist die Rendite bei einer 350.000€ Wohnung?",
                    "Was sind die Steuervorteile bei Neubau-Immobilien?"
                ]
            ),
            AgentSkill(
                id="financial_calculation",
                name="Real Estate Financial Analysis",
                description="Detailed financial calculations including ROI, cash flow, and tax optimization",
                tags=["finance", "calculation", "roi", "cashflow", "taxation"],
                examples=[
                    "Berechne die Rendite für eine Wohnung in Berlin",
                    "Welche Steuervorteile bietet die 5% Sonder-AfA?",
                    "Cashflow-Analyse für 20 Jahre"
                ]
            ),
            AgentSkill(
                id="property_search",
                name="Property Search and Selection",
                description="Finding and evaluating suitable new-construction properties",
                tags=["property", "search", "evaluation", "neubau"],
                examples=[
                    "Finde Neubau-Wohnungen in Hamburg unter 400.000€",
                    "Welche Objekte gibt es in Leipzig?",
                    "A+ Energiestandard Immobilien suchen"
                ]
            ),
            AgentSkill(
                id="knowledge_base_search",
                name="FAQ and Legal Knowledge",
                description="Access to comprehensive FAQ database and German real estate legal information",
                tags=["faq", "legal", "knowledge", "handbooks"],
                examples=[
                    "Was ist das Erbbaurecht?",
                    "Muss ein Kaufvertrag notariell beurkundet werden?",
                    "Welche Kosten fallen bei ImmoAssist an?"
                ]
            ),
            AgentSkill(
                id="market_analysis",
                name="Real Estate Market Analysis",
                description="Current market trends, location analysis, and investment recommendations",
                tags=["market", "analysis", "trends", "location"],
                examples=[
                    "Wie entwickeln sich die Immobilienpreise in Berlin?",
                    "Welche Stadtteile sind als Investment interessant?",
                    "Marktprognose für deutsche Neubau-Immobilien"
                ]
            )
        ]
        
        # Provider information
        provider = AgentProvider(
            organization="ImmoAssist",
            url="https://immoassist.com",
            contact="support@immoassist.com"
        )
        
        # Create the complete agent card
        agent_card = AgentCard(
            name="immoassist_philipp",
            description="Philipp - Personal AI consultant for German real estate investments. Specializes in new-construction properties (250k-500k EUR) with expert team coordination for comprehensive investment advice.",
            url=base_url,
            version="2.0.0",
            capabilities=capabilities,
            authentication=authentication,
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain", "application/json"],
            skills=skills,
            provider=provider,
            documentationUrl=f"{base_url}/docs"
        )
        
        return agent_card
    
    @staticmethod
    def save_card_to_file(agent_card: AgentCard, file_path: str = ".well-known/agent.json") -> None:
        """Save agent card to file for A2A discovery."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(agent_card.to_json())
        
        print(f"A2A Agent Card saved to: {file_path}")
    
    @staticmethod
    def create_agent_discovery_endpoint() -> Dict[str, Any]:
        """Create agent discovery information for A2A protocol."""
        card = ImmoAssistAgentCard.create_card()
        
        return {
            "agent_card": card.to_dict(),
            "discovery_timestamp": datetime.now().isoformat(),
            "protocol_version": "2.0",
            "status": "active"
        }


def generate_agent_card_json(output_file: str = ".well-known/agent.json") -> str:
    """Generate and save A2A agent card for ImmoAssist."""
    
    # Create agent card
    card = ImmoAssistAgentCard.create_card()
    
    # Save to file
    ImmoAssistAgentCard.save_card_to_file(card, output_file)
    
    return card.to_json()


if __name__ == "__main__":
    # Generate agent card for development
    print("Generating ImmoAssist A2A Agent Card...")
    
    card_json = generate_agent_card_json()
    print("\nGenerated Agent Card:")
    print(card_json)
    
    print("\n✅ A2A Agent Card created successfully!")
    print("🔗 Ready for agent-to-agent communication")
    print("📍 Discovery endpoint: /.well-known/agent.json") 