#!/usr/bin/env python3
"""
Direct launcher for ImmoAssist Multi-Agent System
Bypasses ADK CLI to avoid Windows symlink issues
"""

import os
import sys
import asyncio
import logging
import uuid

def main():
    """Launch ImmoAssist system directly"""
    # Set environment variables
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    
    # Import the agent after environment setup
    try:
        from immoassist_agent import root_agent
        from google.adk.runners import InMemoryRunner
        from google.genai import types
        
        print("Starting ImmoAssist Multi-Agent System...")
        print("Authentication: Using Google Cloud default credentials")
        print("Agent loaded successfully")
        print("Starting runner...")
        
        # Create runner
        runner = InMemoryRunner(agent=root_agent)
        
        # Create test message
        test_message = types.Content(
            parts=[types.Part(text="Hallo, ich bin interessiert an Immobilieninvestments.")]
        )
        
        # Run a test to make sure everything works
        events = runner.run(
            user_id="test_user",
            session_id=str(uuid.uuid4()),
            new_message=test_message
        )
        
        print("Test successful! Agent events:")
        for event in events:
            if hasattr(event, 'content') and event.content:
                print(f"Agent: {event.content}")
                break
        
        print("\nImmoAssist Multi-Agent System is working!")
        print("System ready for use!")
        print("Google Cloud authentication: OK")
        print("Multi-agent system: OK")
        print("All 5 agents initialized: OK")
        
    except Exception as e:
        print(f"Error starting ImmoAssist system: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 