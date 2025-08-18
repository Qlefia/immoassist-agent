#!/usr/bin/env python3
"""
Validation script for ImmoAssist prompt refactoring.

Quick validation that all focused prompts are working correctly
and agents are properly initialized with new modular system.
"""

import sys
import traceback
from app.prompts import PromptComposer, validate_all_agents

def main():
    """Validate all agent prompts and report status."""
    
    print("ImmoAssist Prompt System Validation")
    print("=" * 50)
    
    try:
        # List all available agents
        agents = PromptComposer.list_available_agents()
        print(f"SUCCESS: Found {len(agents)} agent types: {', '.join(agents)}")
        
        # Validate each agent
        print("\nAgent Validation Results:")
        results = validate_all_agents()
        
        all_valid = True
        for agent_name, result in results.items():
            status = "SUCCESS" if result["valid"] else "FAILED"
            length = result.get("prompt_length", 0)
            lines = result.get("prompt_lines", 0)
            
            print(f"{status}: {agent_name}: {length} chars, {lines} lines")
            
            if not result["valid"]:
                all_valid = False
                for issue in result.get("issues", []):
                    print(f"   WARNING: {issue}")
        
        # Test agent imports
        print("\nTesting Agent Import...")
        try:
            from app.agent import (
                root_agent, 
                knowledge_specialist, 
                calculator_specialist,
                property_specialist
            )
            print("SUCCESS: All agents imported successfully")
            print(f"SUCCESS: Root agent model: {root_agent.model}")
            print(f"SUCCESS: Root agent name: {root_agent.name}")
            
        except Exception as e:
            print(f"FAILED: Agent import failed: {e}")
            all_valid = False
        
        # Final status
        print("\n" + "=" * 50)
        if all_valid:
            print("ALL VALIDATIONS PASSED - System ready for testing!")
            print("\nNext steps:")
            print("   1. Test with: python run_agent.py")
            print("   2. Verify agent responses and functionality")
            print("   3. Check that all tools work correctly")
            print("   4. Validate memory and conversation flow")
            return 0
        else:
            print("VALIDATION FAILED - Fix issues before testing")
            return 1
            
    except Exception as e:
        print(f"FAILED: Validation script failed: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())