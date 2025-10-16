#!/usr/bin/env python3
"""
Advanced Usage Examples for the Enhanced Research Agent.

This script demonstrates the comprehensive automation capabilities including:
- Advanced browser automation
- GitHub repository management
- File system operations
- Workflow orchestration
- Safety and security controls
"""

import os
import time
import json
from datetime import datetime

# Import the enhanced research agent
from research_agent.enhanced_agent import EnhancedResearchAgent
from research_agent.browser_controller import AdvancedBrowserController
from research_agent.github_controller import AdvancedGitHubController
from research_agent.file_controller import AdvancedFileController
from research_agent.workflow_orchestrator import WorkflowOrchestrator, WorkflowStep
from research_agent.safety_controller import AdvancedSafetyController, SecurityPolicy, RiskLevel


def example_basic_enhanced_research():
    """Example of basic enhanced research capabilities."""
    print("=== Basic Enhanced Research Example ===")
    
    # Initialize enhanced agent
    agent = EnhancedResearchAgent(
        enable_advanced=True,
        safety_config="safety_config.json"
    )
    
    try:
        # Start browser automation
        if agent.start_browser(headless=True):
            print("Browser started successfully")
            
            # Navigate and research a website
            result = agent.navigate_and_research("https://httpbin.org/html")
            if "error" not in result:
                print(f"Research completed: {result['page_info']['title']}")
                print(f"Screenshot saved: {result['screenshot']}")
            else:
                print(f"Research failed: {result['error']}")
        
        # Get safety status
        safety_status = agent.get_safety_status()
        print(f"Safety status: {safety_status}")
        
    except Exception as e:
        print(f"Error in enhanced research: {e}")
    finally:
        agent.close()


def example_github_automation():
    """Example of GitHub automation capabilities."""
    print("\n=== GitHub Automation Example ===")
    
    # Check for GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("GitHub token not found. Set GITHUB_TOKEN environment variable.")
        return
    
    agent = EnhancedResearchAgent(enable_advanced=True)
    
    try:
        # Create a GitHub repository
        repo_result = agent.create_github_repository(
            name=f"research-{int(time.time())}",
            description="Automated research repository",
            private=False
        )
        
        if repo_result.get("success"):
            print(f"Repository created successfully!")
            print(f"URL: {repo_result['repository']['html_url']}")
        else:
            print(f"Repository creation failed: {repo_result.get('error')}")
            
    except Exception as e:
        print(f"GitHub automation error: {e}")
    finally:
        agent.close()


def example_file_system_operations():
    """Example of advanced file system operations."""
    print("\n=== File System Operations Example ===")
    
    agent = EnhancedResearchAgent(enable_advanced=True)
    
    try:
        # Create test directory
        test_dir = "./test_research_data"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create some test files
        test_files = {
            "notes.md": "# Research Notes\n\nThis is a test research file.",
            "data.json": json.dumps({"topic": "AI Research", "date": datetime.now().isoformat()}),
            "todo.txt": "TODO: Complete research\nFIXME: Update documentation"
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(test_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
        
        # Perform file analysis
        analysis = agent.perform_file_analysis(test_dir, "comprehensive")
        
        if "error" not in analysis:
            print(f"File analysis completed:")
            print(f"  Files found: {analysis['file_count']}")
            print(f"  Total size: {analysis['total_size']} bytes")
            print(f"  TODOs found: {len(analysis.get('todos', []))}")
        else:
            print(f"File analysis failed: {analysis['error']}")
            
    except Exception as e:
        print(f"File system operations error: {e}")
    finally:
        agent.close()


def example_workflow_orchestration():
    """Example of workflow orchestration."""
    print("\n=== Workflow Orchestration Example ===")
    
    agent = EnhancedResearchAgent(enable_advanced=True)
    
    try:
        # Create a custom workflow
        workflow_steps = [
            WorkflowStep(
                id="create_dir",
                name="Create Research Directory",
                action="file.create_directory",
                parameters={"path": "./workflow_output"}
            ),
            WorkflowStep(
                id="create_file",
                name="Create Research File",
                action="file.create_file",
                parameters={
                    "path": "./workflow_output/research.md",
                    "content": "# Workflow Research\n\nThis file was created by a workflow."
                }
            ),
            WorkflowStep(
                id="search_content",
                name="Search for Content",
                action="file.search_content",
                parameters={
                    "pattern": "workflow",
                    "directory": "./workflow_output"
                }
            )
        ]
        
        # Register workflow
        agent.workflow_orchestrator.register_workflow(
            "test_workflow",
            "Test Workflow",
            "A simple test workflow",
            workflow_steps
        )
        
        # Execute workflow
        result = agent.execute_workflow("test_workflow", {"topic": "workflow_test"})
        
        if result.get("success"):
            print("Workflow executed successfully!")
            print(f"Execution ID: {result['execution_id']}")
        else:
            print(f"Workflow execution failed: {result.get('error')}")
            
    except Exception as e:
        print(f"Workflow orchestration error: {e}")
    finally:
        agent.close()


def example_safety_controls():
    """Example of safety and security controls."""
    print("\n=== Safety Controls Example ===")
    
    # Initialize safety controller
    safety = AdvancedSafetyController("safety_config.json")
    
    try:
        # Create a security policy
        policy = SecurityPolicy(
            name="research_policy",
            description="Research automation policy",
            allowed_actions={"file.create", "file.read", "browser.navigate"},
            blocked_actions={"file.delete", "system.shutdown"},
            allowed_domains={"httpbin.org", "example.com"},
            blocked_domains={"malicious-site.com"},
            allowed_paths={"./research_data", "./output"},
            blocked_paths={"/system", "/windows"},
            max_file_size=50*1024*1024,  # 50MB
            max_operations_per_minute=30,
            max_concurrent_operations=5,
            require_approval=True,
            risk_threshold=RiskLevel.MEDIUM
        )
        
        # Create and set policy
        safety.create_policy(policy)
        safety.set_policy("research_policy")
        
        # Request operations
        operations = [
            ("file.create", "./research_data/notes.txt"),
            ("browser.navigate", "https://httpbin.org/html"),
            ("file.delete", "./important_file.txt")  # This should be blocked
        ]
        
        for action, resource in operations:
            has_permission, message, operation_id = safety.request_operation(
                user_id="researcher",
                action=action,
                resource=resource
            )
            
            print(f"Operation: {action} on {resource}")
            print(f"  Permission: {has_permission}")
            print(f"  Message: {message}")
            print(f"  Operation ID: {operation_id}")
            print()
        
        # Get pending approvals
        pending = safety.get_pending_approvals()
        print(f"Pending approvals: {len(pending)}")
        
        # Get safety status
        status = safety.get_safety_status()
        print(f"Safety status: {status}")
        
    except Exception as e:
        print(f"Safety controls error: {e}")
    finally:
        safety.cleanup()


def example_comprehensive_research():
    """Example of comprehensive multi-modal research."""
    print("\n=== Comprehensive Research Example ===")
    
    agent = EnhancedResearchAgent(enable_advanced=True)
    
    try:
        # Configure comprehensive research
        research_config = {
            "enable_web_research": True,
            "enable_github_research": True,
            "enable_file_analysis": True,
            "enable_workflow_execution": True,
            "web_urls": ["https://httpbin.org/html", "https://httpbin.org/json"],
            "analysis_directory": "./research_data"
        }
        
        # Create analysis directory
        os.makedirs("./research_data", exist_ok=True)
        
        # Perform comprehensive research
        results = agent.comprehensive_research("Advanced AI Research", research_config)
        
        if results.get("success"):
            print("Comprehensive research completed successfully!")
            print(f"Report saved to: {results['report_path']}")
            
            # Display research phases
            for phase, data in results.get("research_phases", {}).items():
                print(f"\n{phase.replace('_', ' ').title()}:")
                if isinstance(data, dict) and "error" not in data:
                    for key, value in data.items():
                        if isinstance(value, (str, int, float)):
                            print(f"  {key}: {value}")
                elif isinstance(data, list):
                    print(f"  Items: {len(data)}")
        else:
            print(f"Comprehensive research failed: {results.get('error')}")
            
    except Exception as e:
        print(f"Comprehensive research error: {e}")
    finally:
        agent.close()


def example_emergency_controls():
    """Example of emergency controls and monitoring."""
    print("\n=== Emergency Controls Example ===")
    
    agent = EnhancedResearchAgent(enable_advanced=True)
    
    try:
        # Start some operations
        print("Starting operations...")
        agent.start_browser(headless=True)
        
        # Monitor safety status
        print("Monitoring safety status...")
        for i in range(5):
            status = agent.get_safety_status()
            print(f"  Iteration {i+1}: Emergency stop = {status['emergency_stop']}")
            time.sleep(1)
        
        # Demonstrate emergency stop
        print("Triggering emergency stop...")
        agent.emergency_stop("Demonstration emergency stop")
        
        status = agent.get_safety_status()
        print(f"After emergency stop: {status['emergency_stop']}")
        
        # Get audit trail
        audit_trail = agent.get_audit_trail()
        print(f"Audit trail entries: {len(audit_trail)}")
        
    except Exception as e:
        print(f"Emergency controls error: {e}")
    finally:
        agent.close()


def main():
    """Run all examples."""
    print("Enhanced Research Agent - Advanced Capabilities Examples")
    print("=" * 60)
    
    # Set up environment
    os.makedirs("./research_data", exist_ok=True)
    os.makedirs("./workflow_output", exist_ok=True)
    
    # Run examples
    try:
        example_basic_enhanced_research()
        example_github_automation()
        example_file_system_operations()
        example_workflow_orchestration()
        example_safety_controls()
        example_comprehensive_research()
        example_emergency_controls()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        try:
            import shutil
            if os.path.exists("./test_research_data"):
                shutil.rmtree("./test_research_data")
            if os.path.exists("./workflow_output"):
                shutil.rmtree("./workflow_output")
        except Exception:
            pass


if __name__ == "__main__":
    main()
