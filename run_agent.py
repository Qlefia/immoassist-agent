#!/usr/bin/env python3
"""
Simple ADK runner for ImmoAssist agent
"""

import os
import sys
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app

# Setup environment
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west1")

def main():
    """Run the ImmoAssist agent with ADK web interface."""
    
    # Get the directory containing this script, which is the project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agents_dir = script_dir  # Use the project root as the agents directory
    
    print(f"🤖 Starting ImmoAssist Agent...")
    print(f"📁 Agents directory: {agents_dir}")
    print(f"   (Looking for agent packages like 'app' here)")
    print(f"🌐 Web interface will be available at: http://localhost:8000")
    
    try:
        # Create FastAPI app with ADK
        app = get_fast_api_app(
            agents_dir=agents_dir,
            web=True,  # Enable web interface
            allow_origins=["*"],  # Allow all origins for development
        )
        
        # Start server
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print(f"💡 Make sure you have:")
        print(f"   - Google Cloud authentication set up")
        print(f"   - GOOGLE_CLOUD_PROJECT environment variable set")
        print(f"   - Vertex AI API enabled")
        sys.exit(1)

if __name__ == "__main__":
    main() 