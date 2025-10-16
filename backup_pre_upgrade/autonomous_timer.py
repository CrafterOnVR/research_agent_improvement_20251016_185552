#!/usr/bin/env python3  
  
""" >> autonomous_timer.py && echo ARINN Autonomous Goal Timer >> autonomous_timer.py && echo Simple version without Unicode issues >> autonomous_timer.py && echo """  
  
import time  
from datetime import datetime  
  
def get_time_until_next_goal():
    """Get seconds until the next 5-minute boundary (0,5,10,...,55).

    Uses modulo arithmetic to ensure a single trigger exactly at boundaries.
    """
    now = datetime.now()
    seconds_since_hour = now.minute * 60 + now.second
    seconds_until_next = (300 - (seconds_since_hour % 300)) % 300
    return seconds_until_next

# Global agent instance to maintain state
_agent_instance = None

def get_agent_instance():
    """Get or create the persistent agent instance."""
    global _agent_instance
    if _agent_instance is None:
        try:
            from super_enhanced_agent import SuperEnhancedResearchAgent
            _agent_instance = SuperEnhancedResearchAgent(enable_super_intelligence=True)
            print("Created persistent agent instance")
        except ImportError:
            print("Could not import SuperEnhancedResearchAgent")
            return None
    return _agent_instance

def trigger_goal_execution():
    """Trigger actual goal execution in the ARINN agent."""
    try:
        # Get the persistent agent instance
        agent = get_agent_instance()
        if agent is None:
            return False

        # Execute autonomous goal
        try:
            agent._execute_autonomous_goal()
            return True
        except AttributeError:
            print("Agent does not have autonomous goal execution capability")
            return False

    except Exception as e:
        print(f"Failed to trigger goal execution: {e}")
        return False

if __name__ == "__main__":
    while True:
        time_remaining = get_time_until_next_goal()
        if time_remaining == 0:
            print()
            print(f"GOAL TIME: {datetime.now().strftime('%H:%M:%S')}")
            print("ARINN would now select and pursue an autonomous goal")
            print("Possible goals: code optimization, intelligence enhancement, research expansion, etc.")

            # Actually trigger goal execution
            success = trigger_goal_execution()
            if success:
                print("[SUCCESS] Goal execution triggered successfully")
            else:
                print("[FAILED] Goal execution failed")

            print()
        time.sleep(1)
