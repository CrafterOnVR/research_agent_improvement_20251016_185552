"""
Workflow Orchestrator for complex multi-step automation operations.

This module provides comprehensive workflow orchestration capabilities including:
- Multi-step workflow execution
- Conditional logic and branching
- Parallel and sequential operations
- Error handling and recovery
- Workflow templates and reusability
- Progress tracking and monitoring
- Integration with browser, GitHub, and file controllers
"""

import json
import time
import logging
import asyncio
from typing import Optional, Dict, List, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

try:
    # Try relative imports first (for package execution)
    from .browser_controller import AdvancedBrowserController
    from .github_controller import AdvancedGitHubController
    from .file_controller import AdvancedFileController
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from browser_controller import AdvancedBrowserController
    from github_controller import AdvancedGitHubController
    from file_controller import AdvancedFileController


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class StepStatus(Enum):
    """Individual step status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    id: str
    name: str
    action: str
    parameters: Dict[str, Any]
    conditions: List[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout: int = 300  # 5 minutes
    parallel: bool = False
    depends_on: List[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance."""
    id: str
    workflow_id: str
    status: WorkflowStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    steps: List[WorkflowStep] = None
    variables: Dict[str, Any] = None
    error_message: Optional[str] = None
    progress: float = 0.0
    
    def __post_init__(self):
        if self.steps is None:
            self.steps = []
        if self.variables is None:
            self.variables = {}


class WorkflowOrchestrator:
    """Advanced workflow orchestration system."""
    
    def __init__(self, browser_controller: Optional[AdvancedBrowserController] = None,
                 github_controller: Optional[AdvancedGitHubController] = None,
                 file_controller: Optional[AdvancedFileController] = None):
        self.browser_controller = browser_controller
        self.github_controller = github_controller
        self.file_controller = file_controller
        
        # Workflow management
        self.workflows = {}
        self.executions = {}
        self.active_executions = {}
        
        # Execution control
        self.max_concurrent_executions = 5
        self.execution_lock = asyncio.Lock()
        
        # Custom actions registry
        self.custom_actions = {}
        
        # Safety controls
        self.max_execution_time = 3600  # 1 hour
        self.allowed_actions = set()
        self.blocked_actions = set()
    
    def register_workflow(self, workflow_id: str, name: str, description: str,
                         steps: List[WorkflowStep], variables: Dict[str, Any] = None) -> bool:
        """Register a new workflow template."""
        try:
            workflow = {
                "id": workflow_id,
                "name": name,
                "description": description,
                "steps": [asdict(step) for step in steps],
                "variables": variables or {},
                "created_at": datetime.now().isoformat()
            }
            
            self.workflows[workflow_id] = workflow
            return True
        except Exception as e:
            logging.error(f"Failed to register workflow: {e}")
            return False
    
    async def start_execution(self, workflow_id: str, variables: Dict[str, Any] = None,
                       execution_id: Optional[str] = None) -> Optional[str]:
        """Start a workflow execution."""
        if workflow_id not in self.workflows:
            logging.error(f"Workflow not found: {workflow_id}")
            return None
        
        if execution_id is None:
            execution_id = str(uuid.uuid4())
        
        async with self.execution_lock:
            if len(self.active_executions) >= self.max_concurrent_executions:
                logging.warning("Maximum concurrent executions reached")
                return None
        
        try:
            # Create execution instance
            workflow = self.workflows[workflow_id]
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.PENDING,
                start_time=datetime.now(),
                steps=[WorkflowStep(**step) for step in workflow["steps"]],
                variables={**(workflow.get("variables", {})), **(variables or {})}
            )
            
            self.executions[execution_id] = execution
            self.active_executions[execution_id] = execution
            
            # Start execution as an asyncio task
            asyncio.create_task(self._execute_workflow(execution_id))
            
            return execution_id
        except Exception as e:
            logging.error(f"Failed to start execution: {e}")
            return None
    
    async def _execute_workflow(self, execution_id: str):
        """Execute a workflow asynchronously."""
        execution = self.executions.get(execution_id)
        if not execution:
            return
        
        try:
            execution.status = WorkflowStatus.RUNNING
            start_time = time.time()
            
            # Execute steps in order
            for step in execution.steps:
                if execution.status == WorkflowStatus.CANCELLED:
                    break
                
                # Check dependencies
                if not self._check_dependencies(step, execution):
                    step.status = StepStatus.SKIPPED
                    continue
                
                # Execute step
                step.status = StepStatus.RUNNING
                success = await self._execute_step(step, execution)
                
                if success:
                    step.status = StepStatus.COMPLETED
                else:
                    step.status = StepStatus.FAILED
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.status = StepStatus.PENDING
                        # Re-execute step
                        success = await self._execute_step(step, execution)
                        if success:
                            step.status = StepStatus.COMPLETED
                        else:
                            step.status = StepStatus.FAILED
                            execution.status = WorkflowStatus.FAILED
                            break
                    else:
                        execution.status = WorkflowStatus.FAILED
                        break
                
                # Update progress
                execution.progress = (execution.steps.index(step) + 1) / len(execution.steps) * 100
                
                # Check timeout
                if time.time() - start_time > self.max_execution_time:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = "Execution timeout"
                    break
            
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
            
            execution.end_time = datetime.now()
            
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            logging.error(f"Workflow execution failed: {e}")
        finally:
            async with self.execution_lock:
                self.active_executions.pop(execution_id, None)
    
    def _check_dependencies(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Check if step dependencies are satisfied."""
        for dep_id in step.depends_on:
            dep_step = next((s for s in execution.steps if s.id == dep_id), None)
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        return True
    
    async def _execute_step(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute a single workflow step."""
        try:
            # Check action permissions
            if not self._check_action_permissions(step.action):
                logging.warning(f"Action not allowed: {step.action}")
                return False
            
            # Execute action based on type
            if step.action.startswith("browser."):
                return await self._execute_browser_action(step, execution)
            elif step.action.startswith("github."):
                return await self._execute_github_action(step, execution)
            elif step.action.startswith("file."):
                return await self._execute_file_action(step, execution)
            elif step.action in self.custom_actions:
                return await self._execute_custom_action(step, execution)
            else:
                logging.error(f"Unknown action: {step.action}")
                return False
                
        except Exception as e:
            logging.error(f"Step execution failed: {e}")
            return False
    
    async def _execute_browser_action(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute browser-related actions."""
        if not self.browser_controller:
            logging.error("Browser controller not available")
            return False
        
        action = step.action.replace("browser.", "")
        params = step.parameters
        
        try:
            if action == "navigate":
                return await asyncio.to_thread(self.browser_controller.navigate_to, params.get("url"))
            elif action == "click":
                return await asyncio.to_thread(self.browser_controller.click_element,
                    params.get("selector"), 
                    params.get("by", "css")
                )
            elif action == "type":
                return await asyncio.to_thread(self.browser_controller.type_text,
                    params.get("selector"),
                    params.get("text", ""),
                    params.get("by", "css")
                )
            elif action == "fill_form":
                return await asyncio.to_thread(self.browser_controller.fill_form, params.get("form_data", {}))
            elif action == "submit_form":
                return await asyncio.to_thread(self.browser_controller.submit_form,
                    params.get("form_selector"),
                    params.get("submit_button_selector")
                )
            elif action == "screenshot":
                return await asyncio.to_thread(self.browser_controller.take_screenshot, params.get("filename")) is not None
            elif action == "scroll":
                return await asyncio.to_thread(self.browser_controller.scroll_page,
                    params.get("direction", "down"),
                    params.get("amount", 3)
                )
            elif action == "wait":
                return await asyncio.to_thread(self.browser_controller.wait_for_element,
                    params.get("selector"),
                    params.get("by", "css"),
                    params.get("timeout", 10)
                )
            else:
                logging.error(f"Unknown browser action: {action}")
                return False
        except Exception as e:
            logging.error(f"Browser action failed: {e}")
            return False
    
    async def _execute_github_action(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute GitHub-related actions."""
        if not self.github_controller:
            logging.error("GitHub controller not available")
            return False
        
        action = step.action.replace("github.", "")
        params = step.parameters
        
        try:
            if action == "create_repo":
                result = await asyncio.to_thread(self.github_controller.create_repository,
                    params.get("name"),
                    params.get("description", ""),
                    params.get("private", False)
                )
                return result is not None
            elif action == "create_issue":
                result = await asyncio.to_thread(self.github_controller.create_issue,
                    params.get("owner"),
                    params.get("repo"),
                    params.get("title"),
                    params.get("body", ""),
                    params.get("labels", []),
                    params.get("assignees", [])
                )
                return result is not None
            elif action == "create_pr":
                result = await asyncio.to_thread(self.github_controller.create_pull_request,
                    params.get("owner"),
                    params.get("repo"),
                    params.get("title"),
                    params.get("head"),
                    params.get("base"),
                    params.get("body", "")
                )
                return result is not None
            elif action == "clone_repo":
                return await asyncio.to_thread(self.github_controller.clone_repository,
                    params.get("owner"),
                    params.get("repo"),
                    params.get("local_path"),
                    params.get("branch", "main")
                )
            else:
                logging.error(f"Unknown GitHub action: {action}")
                return False
        except Exception as e:
            logging.error(f"GitHub action failed: {e}")
            return False
    
    async def _execute_file_action(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute file system actions."""
        if not self.file_controller:
            logging.error("File controller not available")
            return False
        
        action = step.action.replace("file.", "")
        params = step.parameters
        
        try:
            if action == "create_file":
                return await asyncio.to_thread(self.file_controller.create_file,
                    params.get("path"),
                    params.get("content", "")
                )
            elif action == "write_file":
                return await asyncio.to_thread(self.file_controller.write_file,
                    params.get("path"),
                    params.get("content", "")
                )
            elif action == "copy_file":
                return await asyncio.to_thread(self.file_controller.copy_file,
                    params.get("source"),
                    params.get("destination")
                )
            elif action == "move_file":
                return await asyncio.to_thread(self.file_controller.move_file,
                    params.get("source"),
                    params.get("destination")
                )
            elif action == "delete_file":
                return await asyncio.to_thread(self.file_controller.delete_file, params.get("path"))
            elif action == "create_directory":
                return await asyncio.to_thread(self.file_controller.create_directory, params.get("path"))
            elif action == "search_content":
                results = await asyncio.to_thread(self.file_controller.search_content,
                    params.get("pattern"),
                    params.get("directory"),
                    params.get("file_pattern", "*")
                )
                # Store results in execution variables
                execution.variables[f"{step.id}_results"] = results
                return True
            elif action == "replace_content":
                count = await asyncio.to_thread(self.file_controller.replace_content,
                    params.get("pattern"),
                    params.get("replacement"),
                    params.get("directory"),
                    params.get("file_pattern", "*")
                )
                execution.variables[f"{step.id}_replaced_count"] = count
                return True
            else:
                logging.error(f"Unknown file action: {action}")
                return False
        except Exception as e:
            logging.error(f"File action failed: {e}")
            return False
    
    def _execute_custom_action(self, step: WorkflowStep, execution: WorkflowExecution) -> bool:
        """Execute custom registered actions."""
        action_func = self.custom_actions.get(step.action)
        if not action_func:
            return False
        
        try:
            return action_func(step.parameters, execution.variables)
        except Exception as e:
            logging.error(f"Custom action failed: {e}")
            return False
    
    def register_custom_action(self, action_name: str, action_func: Callable[[Dict, Dict], bool]):
        """Register a custom action function."""
        self.custom_actions[action_name] = action_func
    
    def _check_action_permissions(self, action: str) -> bool:
        """Check if action is allowed."""
        if self.blocked_actions and action in self.blocked_actions:
            return False
        if self.allowed_actions and action not in self.allowed_actions:
            return False
        return True
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status and details."""
        execution = self.executions.get(execution_id)
        if not execution:
            return None
        
        return {
            "id": execution.id,
            "workflow_id": execution.workflow_id,
            "status": execution.status.value,
            "start_time": execution.start_time.isoformat(),
            "end_time": execution.end_time.isoformat() if execution.end_time else None,
            "progress": execution.progress,
            "error_message": execution.error_message,
            "steps": [
                {
                    "id": step.id,
                    "name": step.name,
                    "status": step.status.value,
                    "retry_count": step.retry_count
                }
                for step in execution.steps
            ]
        }
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.CANCELLED
            return True
        
        return False
    
    def pause_execution(self, execution_id: str) -> bool:
        """Pause a running execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.PAUSED
            return True
        
        return False
    
    def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused execution."""
        execution = self.executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status == WorkflowStatus.PAUSED:
            execution.status = WorkflowStatus.RUNNING
            # Restart execution thread
            thread = threading.Thread(target=self._execute_workflow, args=(execution_id,))
            thread.daemon = True
            thread.start()
            return True
        
        return False
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """Get available workflow templates."""
        return [
            {
                "id": workflow_id,
                "name": workflow["name"],
                "description": workflow["description"],
                "steps_count": len(workflow["steps"]),
                "created_at": workflow["created_at"]
            }
            for workflow_id, workflow in self.workflows.items()
        ]
    
    def create_workflow_from_template(self, template_name: str, **kwargs) -> Optional[str]:
        """Create a workflow from a predefined template."""
        templates = {
            "web_scraping": self._create_web_scraping_workflow,
            "github_automation": self._create_github_automation_workflow,
            "file_processing": self._create_file_processing_workflow,
            "research_workflow": self._create_research_workflow
        }
        
        if template_name not in templates:
            return None
        
        return templates[template_name](**kwargs)
    
    def _create_web_scraping_workflow(self, urls: List[str], output_dir: str) -> str:
        """Create a web scraping workflow template."""
        workflow_id = f"web_scraping_{int(time.time())}"
        steps = []
        
        for i, url in enumerate(urls):
            steps.extend([
                WorkflowStep(
                    id=f"navigate_{i}",
                    name=f"Navigate to {url}",
                    action="browser.navigate",
                    parameters={"url": url}
                ),
                WorkflowStep(
                    id=f"screenshot_{i}",
                    name=f"Screenshot {url}",
                    action="browser.screenshot",
                    parameters={"filename": f"{output_dir}/screenshot_{i}.png"}
                ),
                WorkflowStep(
                    id=f"scroll_{i}",
                    name=f"Scroll page {url}",
                    action="browser.scroll",
                    parameters={"direction": "down", "amount": 3}
                )
            ])
        
        self.register_workflow(workflow_id, "Web Scraping", "Automated web scraping workflow", steps)
        return workflow_id
    
    def _create_github_automation_workflow(self, repo_name: str, description: str) -> str:
        """Create a GitHub automation workflow template."""
        workflow_id = f"github_automation_{int(time.time())}"
        steps = [
            WorkflowStep(
                id="create_repo",
                name="Create Repository",
                action="github.create_repo",
                parameters={"name": repo_name, "description": description}
            ),
            WorkflowStep(
                id="create_issue",
                name="Create Initial Issue",
                action="github.create_issue",
                parameters={
                    "owner": "{{github_username}}",
                    "repo": repo_name,
                    "title": "Initial Setup",
                    "body": "Repository created and ready for development"
                }
            )
        ]
        
        self.register_workflow(workflow_id, "GitHub Automation", "Automated GitHub repository setup", steps)
        return workflow_id
    
    def _create_file_processing_workflow(self, source_dir: str, target_dir: str) -> str:
        """Create a file processing workflow template."""
        workflow_id = f"file_processing_{int(time.time())}"
        steps = [
            WorkflowStep(
                id="create_target_dir",
                name="Create Target Directory",
                action="file.create_directory",
                parameters={"path": target_dir}
            ),
            WorkflowStep(
                id="search_files",
                name="Search for Files",
                action="file.search_content",
                parameters={"pattern": "TODO|FIXME", "directory": source_dir}
            ),
            WorkflowStep(
                id="create_report",
                name="Create Report",
                action="file.create_file",
                parameters={
                    "path": f"{target_dir}/report.txt",
                    "content": "File processing report generated"
                }
            )
        ]
        
        self.register_workflow(workflow_id, "File Processing", "Automated file processing workflow", steps)
        return workflow_id
    
    def _create_research_workflow(self, topic: str, output_dir: str) -> str:
        """Create a research workflow template."""
        workflow_id = f"research_{int(time.time())}"
        steps = [
            WorkflowStep(
                id="create_research_dir",
                name="Create Research Directory",
                action="file.create_directory",
                parameters={"path": output_dir}
            ),
            WorkflowStep(
                id="search_github",
                name="Search GitHub Repositories",
                action="github.search_repositories",
                parameters={"query": topic}
            ),
            WorkflowStep(
                id="create_notes",
                name="Create Research Notes",
                action="file.create_file",
                parameters={
                    "path": f"{output_dir}/notes.md",
                    "content": f"# Research Notes: {topic}\n\n"
                }
            )
        ]
        
        self.register_workflow(workflow_id, "Research Workflow", "Automated research workflow", steps)
        return workflow_id
    
    def set_safety_controls(self, allowed_actions: List[str] = None,
                           blocked_actions: List[str] = None,
                           max_execution_time: int = None,
                           max_concurrent_executions: int = None):
        """Configure safety controls."""
        if allowed_actions:
            self.allowed_actions = set(allowed_actions)
        if blocked_actions:
            self.blocked_actions = set(blocked_actions)
        if max_execution_time:
            self.max_execution_time = max_execution_time
        if max_concurrent_executions:
            self.max_concurrent_executions = max_concurrent_executions
