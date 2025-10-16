import time
from super_enhanced_agent import SuperEnhancedResearchAgent

# This test requires an OPENAI_API_KEY to be set as an environment variable.
# If you don't have one, the novel goal generation will be skipped.

def test_goal_generation():
    """
    Tests the goal generation and execution functionality of the SuperEnhancedResearchAgent.
    """
    print("Initializing the Super Enhanced Research Agent for testing...")
    # Initialize the agent
    agent = SuperEnhancedResearchAgent(use_llm=True)

    print("\n" + "="*50)
    print("Starting goal generation and execution test...")
    print("="*50 + "\n")

    # We will run the goal generation 10 times to have a good chance of seeing a novel goal.
    for i in range(10):
        print(f"--- Running goal generation cycle {i+1}/10 ---")
        agent._generate_and_execute_goal()
        print("\n")
        time.sleep(2) # Add a small delay between cycles

    print("="*50)
    print("Goal generation and execution test finished.")
    print("="*50 + "\n")

    # Print the goal history
    print("--- Goal History ---")
    for i, goal_result in enumerate(agent.goal_history):
        goal = goal_result['goal']
        result = goal_result['result']
        novel_str = " (Novel)" if goal.get('is_novel') else ""
        success_str = "SUCCESS" if result.get('success') else "FAILED"
        print(f"Goal {i+1}{novel_str}: [{goal['category']}] {goal['description']} -> {success_str}")

if __name__ == "__main__":
    test_goal_generation()
