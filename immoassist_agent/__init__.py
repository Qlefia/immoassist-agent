"""
ImmoAssist AI Agent

ADK-compatible agent for German real estate consulting,
specializing in new construction investments.
"""

# Copyright 2025 ImmoAssist Agent Development
# ADK-compatible agent initialization

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print initialization status
print("✅ ImmoAssist ADK Agent loading...")

# Check if RAG is configured
if os.getenv('RAG_CORPUS'):
    print(f"📚 RAG Corpus: {os.getenv('RAG_CORPUS')}")
else:
    print("📁 Using local FAQ fallback search")

# Export the multi-agent system and creation function
from .multi_agent_architecture import create_immoassist_multi_agent_system

# Create the root agent instance
root_agent = create_immoassist_multi_agent_system()

# For backward compatibility, also export the factory function
__version__ = "1.0.1"
__all__ = ['root_agent', 'create_immoassist_multi_agent_system']