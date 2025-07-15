#!/usr/bin/env python3
"""
Simple ADK runner for ImmoAssist agent
"""

import os
import sys
from pathlib import Path

# Import the app package to apply Windows Path compatibility patch
import app

import uvicorn
from dotenv import load_dotenv
from google.adk.cli.fast_api import get_fast_api_app

# Load environment variables from .env file
load_dotenv()

# Setup environment
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "europe-west3")


def main():
    """Run the ImmoAssist agent with ADK web interface."""

    # Get the directory containing this script, which is the project root
    script_dir = Path(__file__).resolve().parent
    agents_dir = script_dir  # Use the project root as the agents directory

    print("Starting ImmoAssist Agent...")
    print(f"Agents directory: {agents_dir}")
    print("   (Looking for agent packages like 'app' here)")
    print(" Web interface will be available at: http://localhost:8000")

    try:
        # Create FastAPI app with ADK
        app = get_fast_api_app(
            agents_dir=agents_dir,
            web=True,  # Enable web interface
            allow_origins=["*"],  # Allow all origins for development
        )

        # Get port from environment variable (Cloud Run requires PORT)
        port = int(os.environ.get("PORT", 8000))
        # Start server
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        print("💡 Make sure you have:")
        print("   - Google Cloud authentication set up")
        print("   - GOOGLE_CLOUD_PROJECT environment variable set")
        print("   - Vertex AI API enabled")
        sys.exit(1)


if __name__ == "__main__":
    main()
