"""
Enhanced Research Agent with comprehensive automation capabilities.

This module integrates all advanced controllers to provide:
- Advanced browser automation
- Comprehensive GitHub control
- Extensive file system management
- Workflow orchestration
- Advanced safety controls
- Multi-modal research capabilities
"""

import os
import time
import logging
from typing import Optional, Dict, List, Any, Union
from datetime import datetime

try:
    # Try relative imports first (for package execution)
    from .browser_controller import AdvancedBrowserController
    from .github_controller import AdvancedGitHubController
    from .file_controller import AdvancedFileController
    from .workflow_orchestrator import WorkflowOrchestrator, WorkflowStep
    from .safety_controller import AdvancedSafetyController, RiskLevel
    from .agent import ResearchAgent
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from browser_controller import AdvancedBrowserController
    from github_controller import AdvancedGitHubController
    from file_controller import AdvancedFileController
    from workflow_orchestrator import WorkflowOrchestrator, WorkflowStep
    from safety_controller import AdvancedSafetyController, RiskLevel
    from agent import ResearchAgent


class EnhancedResearchAgent(ResearchAgent):
    """Enhanced research agent with comprehensive automation capabilities."""
    
    def __init__(self, data_dir: Optional[str] = None, use_llm: bool = True, 
                 max_results: int = 10, git_manager: Optional[Any] = None, 
                 auto_commit: bool = False, enable_advanced: bool = True,
                 safety_config: Optional[str] = None):
        
        # Initialize base agent
        super().__init__(data_dir, use_llm, max_results, git_manager, auto_commit)
        
        self.enable_advanced = enable_advanced
        
        # Initialize advanced controllers
        self.browser_controller = None
        self.github_controller = None
        self.file_controller = None
        self.workflow_orchestrator = None
        self.safety_controller = None
        
        if enable_advanced:
            self._initialize_advanced_controllers(safety_config)
    
    def _initialize_advanced_controllers(self, safety_config: Optional[str] = None):
        """Initialize all advanced controllers."""
        try:
            # Initialize safety controller first
            self.safety_controller = AdvancedSafetyController(safety_config)
            
            # Initialize browser controller
            self.browser_controller = AdvancedBrowserController(
                driver_type="chrome",
                headless=True,
                enable_recording=False
            )
            
            # Initialize GitHub controller
            github_token = os.getenv("GITHUB_TOKEN")
            github_username = os.getenv("GITHUB_USERNAME")
            if github_token:
                self.github_controller = AdvancedGitHubController(
                    token=github_token,
                    username=github_username
                )
            
            # Initialize file controller
            self.file_controller = AdvancedFileController(
                base_path=self.data_dir,
                enable_watching=True
            )
            
            # Initialize workflow orchestrator
            self.workflow_orchestrator = WorkflowOrchestrator(
                browser_controller=self.browser_controller,
                github_controller=self.github_controller,
                file_controller=self.file_controller
            )
            
            logging.info("Advanced controllers initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize advanced controllers: {e}")
            self.enable_advanced = False
    
    def start_browser(self, headless: bool = True, driver_type: str = "chrome") -> bool:
        """Start browser automation."""
        if not self.enable_advanced or not self.browser_controller:
            return False
        
        try:
            self.browser_controller.headless = headless
            self.browser_controller.driver_type = driver_type
            return self.browser_controller.start()
        except Exception as e:
            logging.error(f"Failed to start browser: {e}")
            return False
    
    def navigate_and_research(self, url: str, research_depth: str = "standard") -> Dict[str, Any]:
        """Navigate to URL and perform comprehensive research."""
        if not self.enable_advanced or not self.browser_controller:
            return {"error": "Advanced capabilities not available"}
        
        # Check safety permissions
        if self.safety_controller:
            has_permission, message, operation_id = self.safety_controller.request_operation(
                user_id="research_agent",
                action="browser.navigate",
                resource=url
            )
            if not has_permission:
                return {"error": f"Permission denied: {message}"}
        
        try:
            # Navigate to URL
            if not self.browser_controller.navigate_to(url):
                return {"error": "Failed to navigate to URL"}
            
            # Get page information
            page_info = self.browser_controller.get_page_info()
            
            # Take screenshot
            screenshot_path = self.browser_controller.take_screenshot()
            
            # Scroll and capture more content
            self.browser_controller.scroll_page("down", 3)
            
            # Get network logs
            network_logs = self.browser_controller.get_network_logs()
            
            # Store research data
            research_data = {
                "url": url,
                "page_info": page_info,
                "screenshot": screenshot_path,
                "network_logs": network_logs,
                "timestamp": datetime.now().isoformat(),
                "research_depth": research_depth
            }
            
            # Save to database
            topic_id = self.db.get_or_create_topic("web_research")
            content = f"Research data for {url}\n\nPage Title: {page_info.get('title', 'N/A')}\nNetwork Requests: {len(network_logs)}"
            
            added, doc_id = self.db.add_document(
                topic_id, url, page_info.get('title', 'Web Research'), 
                content, created_at=datetime.now().isoformat()
            )
            
            if added:
                self.db.add_snippets_from_text(topic_id, doc_id, content, created_at=datetime.now().isoformat())
            
            # Complete safety operation
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, True, research_data)
            
            return research_data
            
        except Exception as e:
            logging.error(f"Navigation and research failed: {e}")
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, False, {"error": str(e)})
            return {"error": str(e)}
    
    def create_github_repository(self, name: str, description: str = "", 
                                private: bool = False) -> Dict[str, Any]:
        """Create a GitHub repository with comprehensive setup."""
        if not self.enable_advanced or not self.github_controller:
            return {"error": "GitHub capabilities not available"}
        
        # Check safety permissions
        if self.safety_controller:
            has_permission, message, operation_id = self.safety_controller.request_operation(
                user_id="research_agent",
                action="github.create_repo",
                resource=f"https://github.com/{self.github_controller.username}/{name}"
            )
            if not has_permission:
                return {"error": f"Permission denied: {message}"}
        
        try:
            # Create repository
            repo_data = self.github_controller.create_repository(name, description, private)
            if not repo_data:
                return {"error": "Failed to create repository"}
            
            # Create initial files
            readme_content = f"# {name}\n\n{description}\n\n## Research Notes\n\nThis repository was created by the Enhanced Research Agent."
            self.github_controller.create_file(
                self.github_controller.username, name, "README.md", 
                readme_content, "Initial README"
            )
            
            # Create initial issue
            self.github_controller.create_issue(
                self.github_controller.username, name,
                "Initial Research Setup",
                "Repository created and ready for research activities."
            )
            
            # Complete safety operation
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, True, repo_data)
            
            return {
                "success": True,
                "repository": repo_data,
                "readme_created": True,
                "initial_issue_created": True
            }
            
        except Exception as e:
            logging.error(f"GitHub repository creation failed: {e}")
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, False, {"error": str(e)})
            return {"error": str(e)}
    
    def perform_file_analysis(self, directory: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Perform comprehensive file system analysis."""
        if not self.enable_advanced or not self.file_controller:
            return {"error": "File system capabilities not available"}
        
        # Check safety permissions
        if self.safety_controller:
            has_permission, message, operation_id = self.safety_controller.request_operation(
                user_id="research_agent",
                action="file.analyze",
                resource=directory
            )
            if not has_permission:
                return {"error": f"Permission denied: {message}"}
        
        try:
            analysis_results = {
                "directory": directory,
                "timestamp": datetime.now().isoformat(),
                "analysis_type": analysis_type
            }
            
            # Get directory tree
            tree = self.file_controller.get_directory_tree(directory, max_depth=5)
            analysis_results["directory_tree"] = tree
            
            # Find files by pattern
            patterns = ["*.py", "*.md", "*.txt", "*.json", "*.yaml", "*.yml"]
            for pattern in patterns:
                files = self.file_controller.find_files(pattern, directory)
                analysis_results[f"files_{pattern.replace('*', '').replace('.', '')}"] = files
            
            # Search for TODO/FIXME comments
            todo_results = self.file_controller.search_content(
                r"TODO|FIXME|NOTE|HACK", directory, "*.py"
            )
            analysis_results["todos"] = todo_results
            
            # Get file statistics
            all_files = self.file_controller.find_files("*", directory)
            analysis_results["file_count"] = len(all_files)
            
            # Calculate total size
            total_size = 0
            for file_path in all_files:
                try:
                    file_info = self.file_controller.get_file_info(file_path)
                    if file_info:
                        total_size += file_info["size"]
                except Exception:
                    continue
            
            analysis_results["total_size"] = total_size
            
            # Save analysis results
            results_file = os.path.join(directory, "analysis_results.json")
            self.file_controller.create_file(results_file, str(analysis_results))
            
            # Complete safety operation
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, True, analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logging.error(f"File analysis failed: {e}")
            if self.safety_controller and operation_id:
                self.safety_controller.complete_operation(operation_id, False, {"error": str(e)})
            return {"error": str(e)}
    
    def execute_workflow(self, workflow_name: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a predefined or custom workflow."""
        if not self.enable_advanced or not self.workflow_orchestrator:
            return {"error": "Workflow capabilities not available"}
        
        try:
            # Create workflow from template if it doesn't exist
            if workflow_name not in [w["id"] for w in self.workflow_orchestrator.get_workflow_templates()]:
                if workflow_name == "research_workflow":
                    workflow_id = self.workflow_orchestrator.create_workflow_from_template(
                        "research_workflow", 
                        topic=variables.get("topic", "research"),
                        output_dir=variables.get("output_dir", "./research_output")
                    )
                elif workflow_name == "web_automation":
                    workflow_id = self.workflow_orchestrator.create_workflow_from_template(
                        "web_scraping",
                        urls=variables.get("urls", []),
                        output_dir=variables.get("output_dir", "./scraped_data")
                    )
                else:
                    return {"error": f"Unknown workflow: {workflow_name}"}
            else:
                workflow_id = workflow_name
            
            # Start workflow execution
            execution_id = self.workflow_orchestrator.start_execution(workflow_id, variables)
            if not execution_id:
                return {"error": "Failed to start workflow execution"}
            
            # Monitor execution
            max_wait_time = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                status = self.workflow_orchestrator.get_execution_status(execution_id)
                if status["status"] in ["completed", "failed", "cancelled"]:
                    break
                time.sleep(5)
            
            return {
                "execution_id": execution_id,
                "status": status,
                "success": status["status"] == "completed"
            }
            
        except Exception as e:
            logging.error(f"Workflow execution failed: {e}")
            return {"error": str(e)}
    
    def comprehensive_research(self, topic: str, research_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform comprehensive multi-modal research."""
        if not self.enable_advanced:
            # Fall back to standard research
            return super().run(topic)
        
        config = research_config or {}
        results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "research_phases": {}
        }
        
        try:
            # Phase 1: Web Research
            if config.get("enable_web_research", True):
                print(f"Phase 1: Web research for '{topic}'")
                web_urls = config.get("web_urls", [])
                for url in web_urls:
                    web_result = self.navigate_and_research(url)
                    results["research_phases"]["web_research"] = web_result
            
            # Phase 2: GitHub Research
            if config.get("enable_github_research", True) and self.github_controller:
                print(f"Phase 2: GitHub research for '{topic}'")
                github_results = self.github_controller.search_repositories(topic)
                results["research_phases"]["github_research"] = {
                    "repositories_found": len(github_results),
                    "repositories": github_results[:10]  # Top 10
                }
            
            # Phase 3: File System Analysis
            if config.get("enable_file_analysis", True):
                print(f"Phase 3: File system analysis for '{topic}'")
                analysis_dir = config.get("analysis_directory", self.data_dir)
                file_analysis = self.perform_file_analysis(analysis_dir)
                results["research_phases"]["file_analysis"] = file_analysis
            
            # Phase 4: Workflow Execution
            if config.get("enable_workflow_execution", True):
                print(f"Phase 4: Workflow execution for '{topic}'")
                workflow_result = self.execute_workflow(
                    "research_workflow",
                    {"topic": topic, "output_dir": f"./research_output/{topic}"}
                )
                results["research_phases"]["workflow_execution"] = workflow_result
            
            # Phase 5: Generate Report
            print(f"Phase 5: Generating comprehensive report for '{topic}'")
            report_content = self._generate_comprehensive_report(results)
            
            # Save report
            report_path = f"./research_output/{topic}/comprehensive_report.md"
            if self.file_controller:
                self.file_controller.create_file(report_path, report_content)
            
            results["report_path"] = report_path
            results["success"] = True
            
            return results
            
        except Exception as e:
            logging.error(f"Comprehensive research failed: {e}")
            results["error"] = str(e)
            results["success"] = False
            return results
    
    def _generate_comprehensive_report(self, research_results: Dict[str, Any]) -> str:
        """Generate a comprehensive research report."""
        report = f"""# Comprehensive Research Report

## Topic: {research_results['topic']}
## Generated: {research_results['timestamp']}

"""
        
        for phase, data in research_results.get("research_phases", {}).items():
            report += f"## {phase.replace('_', ' ').title()}\n\n"
            
            if isinstance(data, dict):
                if "error" in data:
                    report += f"**Error:** {data['error']}\n\n"
                else:
                    for key, value in data.items():
                        report += f"**{key}:** {value}\n"
            else:
                report += f"{data}\n"
            
            report += "\n"
        
        return report
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status."""
        if not self.safety_controller:
            return {"error": "Safety controller not available"}
        
        return self.safety_controller.get_safety_status()
    
    def get_audit_trail(self, **kwargs) -> List[Dict[str, Any]]:
        """Get security audit trail."""
        if not self.safety_controller:
            return []
        
        return self.safety_controller.get_audit_trail(**kwargs)
    
    def emergency_stop(self, reason: str = "Manual emergency stop"):
        """Trigger emergency stop."""
        if self.safety_controller:
            self.safety_controller.emergency_stop(reason)
    
    def close(self):
        """Clean up all resources."""
        # Close base agent
        super().close()
        
        # Close advanced controllers
        if self.browser_controller:
            self.browser_controller.close()
        
        if self.file_controller:
            self.file_controller.stop_watching()
        
        if self.safety_controller:
            self.safety_controller.cleanup()
        
        logging.info("Enhanced research agent closed successfully")
