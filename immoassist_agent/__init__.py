"""
ImmoAssist AI Agent

Production-ready ADK-compatible agent for German real estate consulting,
specializing in new construction investments with multi-agent architecture.

This package provides:
- Multi-agent system with specialized domain experts
- Vertex AI integration for RAG and model orchestration
- Session management and state persistence
- Enterprise-grade error handling and logging
- A2A protocol support for inter-agent communication
"""

# Copyright 2025 ImmoAssist Agent Development Team
# Licensed under the Apache License, Version 2.0

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Configure logging for package initialization
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Package metadata
__version__ = "1.0.0"
__author__ = "ImmoAssist Development Team"
__email__ = "dev@immoassist.de"
__license__ = "Apache-2.0"

# Print initialization status
logger.info("ImmoAssist ADK Agent loading...")

# Check RAG configuration
rag_corpus: Optional[str] = os.getenv('RAG_CORPUS')
if rag_corpus:
    logger.info(f"RAG Corpus configured: {rag_corpus}")
else:
    logger.info("Using local FAQ fallback search (RAG not configured)")

# Check Google Cloud configuration  
project_id: Optional[str] = os.getenv('GOOGLE_CLOUD_PROJECT')
if project_id:
    logger.info(f"Google Cloud Project: {project_id}")
else:
    logger.warning("Google Cloud Project not configured")

# Import and create the multi-agent system
try:
    from .multi_agent_architecture import create_immoassist_multi_agent_system
    
    # Create the root agent instance for ADK compatibility
    root_agent = create_immoassist_multi_agent_system()
    
    logger.info("Multi-agent system initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize multi-agent system: {str(e)}")
    raise ImportError(f"ImmoAssist agent initialization failed: {str(e)}") from e

# Export public API
__all__ = [
    'root_agent',
    'create_immoassist_multi_agent_system',
    '__version__',
    '__author__',
    '__email__',
    '__license__'
]