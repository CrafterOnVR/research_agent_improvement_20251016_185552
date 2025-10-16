"""
Advanced Automation Engine for Research Agent.

This module provides sophisticated automation capabilities that can learn,
adapt, and optimize operations without requiring external AI models.
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import asyncio


@dataclass
class AutomationTask:
    """Represents an automation task."""
    id: str
    name: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int
    dependencies: List[str]
    estimated_duration: int
    created_at: datetime
    status: str = "pending"
    attempts: int = 0
    max_attempts: int = 3
    result: Any = None
    error: str = None


@dataclass
class AutomationRule:
    """Represents an automation rule."""
    id: str
    name: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    priority: int
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0


@dataclass
class PerformanceMetrics:
    """Performance metrics for automation."""
    task_count: int
    success_rate: float
    average_duration: float
    error_rate: float
    throughput: float
    resource_usage: Dict[str, float]


class AdvancedAutomationEngine:
    """Advanced automation engine with learning capabilities."""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.task_queue = asyncio.Queue()
        self.workers = []
        self.running = False
        
        # Task management
        self.tasks = {}
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Automation rules
        self.rules = {}
        self.rule_engine = RuleEngine()
        
        # Learning system
        self.learning_system = LearningSystem()
        
        # Performance tracking
        self.metrics = PerformanceMetrics(
            task_count=0,
            success_rate=0.0,
            average_duration=0.0,
            error_rate=0.0,
            throughput=0.0,
            resource_usage={}
        )
        
        # Optimization
        self.optimization_engine = OptimizationEngine()
        
    async def start(self):
        """Start the automation engine."""
        self.running = True
        
        # Start worker tasks
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker_loop())
            self.workers.append(worker)
        
        # Start rule engine
        self.rule_engine.start()
        
        # Start learning system
        self.learning_system.start()
        
        logging.info(f"Automation engine started with {self.max_workers} workers")
    
    async def stop(self):
        """Stop the automation engine."""
        self.running = False
        
        # Cancel worker tasks
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        
        # Stop rule engine
        self.rule_engine.stop()
        
        # Stop learning system
        self.learning_system.stop()
        
        logging.info("Automation engine stopped")
    
    async def submit_task(self, task: AutomationTask) -> str:
        """Submit a task for execution."""
        self.tasks[task.id] = task
        await self.task_queue.put(task)
        
        # Check for applicable rules
        await self._check_rules_for_task(task)
        
        logging.info(f"Task submitted: {task.name} (ID: {task.id})")
        return task.id
    
    def create_task(self, name: str, task_type: str, parameters: Dict[str, Any], 
                   priority: int = 5, dependencies: List[str] = None) -> AutomationTask:
        """Create a new automation task."""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"
        
        task = AutomationTask(
            id=task_id,
            name=name,
            task_type=task_type,
            parameters=parameters,
            priority=priority,
            dependencies=dependencies or [],
            estimated_duration=self._estimate_duration(task_type, parameters),
            created_at=datetime.now()
        )
        
        return task
    
    def add_rule(self, rule: AutomationRule):
        """Add an automation rule."""
        self.rules[rule.id] = rule
        self.rule_engine.add_rule(rule)
        logging.info(f"Rule added: {rule.name}")
    
    async def _worker_loop(self):
        """Worker task loop."""
        while self.running:
            try:
                # Get next task
                task = await self.task_queue.get()
                
                # Check dependencies
                if not self._check_dependencies(task):
                    # Re-queue task for later
                    await self.task_queue.put(task)
                    await asyncio.sleep(1)
                    continue
                
                # Execute task
                await self._execute_task(task)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Worker error: {e}")
    
    async def _execute_task(self, task: AutomationTask):
        """Execute a task."""
        task.status = "running"
        start_time = time.time()
        
        try:
            # Get task handler
            handler = self._get_task_handler(task.task_type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.task_type}")
            
            # Execute task
            result = await handler(task.parameters)
            task.result = result
            task.status = "completed"
            
            # Update metrics
            duration = time.time() - start_time
            self._update_metrics(task, duration, success=True)
            
            # Move to completed
            self.completed_tasks.append(task)
            
            # Trigger dependent tasks
            await self._trigger_dependent_tasks(task)
            
            # Learn from success
            self.learning_system.learn_from_success(task, duration)
            
            logging.info(f"Task completed: {task.name} in {duration:.2f}s")
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            task.attempts += 1
            
            # Update metrics
            duration = time.time() - start_time
            self._update_metrics(task, duration, success=False)
            
            # Retry if attempts remaining
            if task.attempts < task.max_attempts:
                task.status = "pending"
                await self.task_queue.put(task)
                logging.warning(f"Task failed, retrying: {task.name} (attempt {task.attempts})")
            else:
                self.failed_tasks.append(task)
                logging.error(f"Task failed permanently: {task.name} - {e}")
            
            # Learn from failure
            self.learning_system.learn_from_failure(task, str(e))
    
    def _get_task_handler(self, task_type: str) -> Optional[Callable]:
        """Get task handler for task type."""
        handlers = {
            "web_scraping": self._handle_web_scraping,
            "data_processing": self._handle_data_processing,
            "file_operations": self._handle_file_operations,
            "github_operations": self._handle_github_operations,
            "analysis": self._handle_analysis,
            "reporting": self._handle_reporting,
            "optimization": self._handle_optimization
        }
        
        return handlers.get(task_type)
    
    async def _handle_web_scraping(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web scraping tasks."""
        url = parameters.get("url")
        selectors = parameters.get("selectors", [])
        
        # Simulate web scraping
        await asyncio.sleep(2) # Simulate network latency
        result = {
            "url": url,
            "scraped_data": f"Data from {url}",
            "elements_found": len(selectors),
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    async def _handle_data_processing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data processing tasks."""
        data = parameters.get("data", [])
        operation = parameters.get("operation", "analyze")
        
        await asyncio.sleep(1) # Simulate processing time
        
        if operation == "analyze":
            result = {
                "count": len(data),
                "summary": f"Processed {len(data)} items",
                "timestamp": datetime.now().isoformat()
            }
        elif operation == "filter":
            filter_criteria = parameters.get("filter_criteria", {})
            filtered_data = [item for item in data if self._matches_criteria(item, filter_criteria)]
            result = {
                "original_count": len(data),
                "filtered_count": len(filtered_data),
                "filtered_data": filtered_data
            }
        else:
            result = {"status": "unknown_operation"}
        
        return result
    
    async def _handle_file_operations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operation tasks."""
        operation = parameters.get("operation")
        file_path = parameters.get("file_path")
        
        await asyncio.sleep(0.5) # Simulate disk I/O
        
        if operation == "create":
            content = parameters.get("content", "")
            with open(file_path, "w") as f:
                f.write(content)
            result = {"status": "created", "file_path": file_path}
        elif operation == "read":
            with open(file_path, "r") as f:
                content = f.read()
            result = {"status": "read", "content": content}
        elif operation == "delete":
            os.remove(file_path)
            result = {"status": "deleted", "file_path": file_path}
        else:
            result = {"status": "unknown_operation"}
        
        return result
    
    async def _handle_github_operations(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GitHub operation tasks."""
        operation = parameters.get("operation")
        
        await asyncio.sleep(1.5) # Simulate API calls
        
        if operation == "create_repo":
            result = {
                "status": "repository_created",
                "repo_name": parameters.get("repo_name"),
                "url": f"https://github.com/user/{parameters.get('repo_name')}"
            }
        elif operation == "create_issue":
            result = {
                "status": "issue_created",
                "issue_number": 1,
                "title": parameters.get("title")
            }
        else:
            result = {"status": "unknown_operation"}
        
        return result
    
    async def _handle_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis tasks."""
        data = parameters.get("data", [])
        analysis_type = parameters.get("analysis_type", "basic")
        
        await asyncio.sleep(1) # Simulate analysis time
        
        if analysis_type == "statistical":
            result = {
                "mean": sum(data) / len(data) if data else 0,
                "count": len(data),
                "analysis_type": "statistical"
            }
        elif analysis_type == "pattern":
            result = {
                "patterns_found": len(set(data)),
                "unique_items": len(set(data)),
                "analysis_type": "pattern"
            }
        else:
            result = {"analysis_type": "basic", "data_count": len(data)}
        
        return result
    
    async def _handle_reporting(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle reporting tasks."""
        data = parameters.get("data", {})
        report_type = parameters.get("report_type", "summary")
        
        await asyncio.sleep(0.5) # Simulate report generation
        
        if report_type == "summary":
            result = {
                "report": f"Summary report generated at {datetime.now()}",
                "data_points": len(data),
                "report_type": "summary"
            }
        elif report_type == "detailed":
            result = {
                "report": f"Detailed report with {len(data)} sections",
                "sections": list(data.keys()),
                "report_type": "detailed"
            }
        else:
            result = {"report_type": "unknown", "data": data}
        
        return result
    
    async def _handle_optimization(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Handle optimization tasks."""
        target = parameters.get("target")
        optimization_type = parameters.get("optimization_type", "performance")
        
        await asyncio.sleep(2) # Simulate optimization process
        
        if optimization_type == "performance":
            result = {
                "optimization": "Performance optimization applied",
                "improvement": "15% faster execution",
                "optimization_type": "performance"
            }
        elif optimization_type == "resource":
            result = {
                "optimization": "Resource usage optimized",
                "memory_reduction": "20% less memory usage",
                "optimization_type": "resource"
            }
        else:
            result = {"optimization_type": "unknown", "target": target}
        
        return result
    
    def _check_dependencies(self, task: AutomationTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            if dep_id not in [t.id for t in self.completed_tasks]:
                return False
        return True
    
    async def _trigger_dependent_tasks(self, completed_task: AutomationTask):
        """Trigger tasks that depend on the completed task."""
        for task in self.tasks.values():
            if completed_task.id in task.dependencies:
                if task.status == "pending":
                    # Re-queue task
                    await self.task_queue.put(task)
    
    def _estimate_duration(self, task_type: str, parameters: Dict[str, Any]) -> int:
        """Estimate task duration based on type and parameters."""
        base_durations = {
            "web_scraping": 30,
            "data_processing": 10,
            "file_operations": 5,
            "github_operations": 15,
            "analysis": 20,
            "reporting": 10,
            "optimization": 25
        }
        
        base_duration = base_durations.get(task_type, 10)
        
        # Adjust based on parameters
        if "data" in parameters and isinstance(parameters["data"], list):
            base_duration += len(parameters["data"]) * 0.1
        
        return int(base_duration)
    
    def _update_metrics(self, task: AutomationTask, duration: float, success: bool):
        """Update performance metrics."""
        self.metrics.task_count += 1
        
        # Update success rate
        total_completed = len(self.completed_tasks) + len(self.failed_tasks)
        if total_completed > 0:
            self.metrics.success_rate = len(self.completed_tasks) / total_completed
        
        # Update average duration
        if self.metrics.task_count > 0:
            self.metrics.average_duration = (
                (self.metrics.average_duration * (self.metrics.task_count - 1) + duration) 
                / self.metrics.task_count
            )
        
        # Update error rate
        if total_completed > 0:
            self.metrics.error_rate = len(self.failed_tasks) / total_completed
        
        # Update throughput (tasks per minute)
        if duration > 0:
            self.metrics.throughput = 60 / duration
    
    def _check_rules_for_task(self, task: AutomationTask):
        """Check if any rules should be triggered for this task."""
        for rule in self.rules.values():
            if rule.enabled and self._evaluate_condition(rule.condition, task):
                self._execute_rule(rule, task)
    
    def _evaluate_condition(self, condition: str, task: AutomationTask) -> bool:
        """Evaluate rule condition."""
        try:
            context = {
                "task_type": task.task_type,
                "priority": task.priority,
            }
            return eval(condition, {"__builtins__": {}}, context)
        except Exception as e:
            logging.error(f"Error evaluating condition '{condition}': {e}")
            return False
    
    async def _execute_rule(self, rule: AutomationRule, task: AutomationTask):
        """Execute automation rule."""
        rule.last_triggered = datetime.now()
        rule.trigger_count += 1
        
        if rule.action == "create_followup_task":
            followup_task = self.create_task(
                name=f"Followup for {task.name}",
                task_type=rule.parameters.get("task_type", "analysis"),
                parameters=rule.parameters.get("parameters", {}),
                priority=rule.parameters.get("priority", 5)
            )
            await self.submit_task(followup_task)
        
        logging.info(f"Rule executed: {rule.name} for task {task.name}")
    
    def _matches_criteria(self, item: Any, criteria: Dict[str, Any]) -> bool:
        """Check if item matches filter criteria."""
        for key, value in criteria.items():
            if hasattr(item, key):
                if getattr(item, key) != value:
                    return False
            elif isinstance(item, dict):
                if item.get(key) != value:
                    return False
            else:
                return False
        return True
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "name": task.name,
            "status": task.status,
            "attempts": task.attempts,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at.isoformat()
        }
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get list of currently active tasks (running or pending)."""
        active_tasks = []
        
        # Get tasks from the main tasks dictionary
        for task in self.tasks.values():
            if task.status in ["running", "pending"]:
                active_tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "task_type": task.task_type,
                    "status": task.status,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat(),
                    "attempts": task.attempts,
                    "parameters": task.parameters
                })
        
        return active_tasks
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return asdict(self.metrics)
    
    def optimize_performance(self):
        """Optimize automation performance."""
        return self.optimization_engine.optimize(self.metrics, self.tasks)


class RuleEngine:
    """Rule engine for automation."""
    
    def __init__(self):
        self.rules = []
        self.running = False
    
    def start(self):
        """Start rule engine."""
        self.running = True
    
    def stop(self):
        """Stop rule engine."""
        self.running = False
    
    def add_rule(self, rule: AutomationRule):
        """Add rule to engine."""
        self.rules.append(rule)


class LearningSystem:
    """Learning system for automation optimization."""
    
    def __init__(self):
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        self.performance_history = []
    
    def start(self):
        """Start learning system."""
        pass
    
    def stop(self):
        """Stop learning system."""
        pass
    
    def learn_from_success(self, task: AutomationTask, duration: float):
        """Learn from successful task execution."""
        pattern = self._extract_pattern(task)
        self.success_patterns[pattern].append(duration)
    
    def learn_from_failure(self, task: AutomationTask, error: str):
        """Learn from failed task execution."""
        pattern = self._extract_pattern(task)
        self.failure_patterns[pattern].append(error)
    
    def _extract_pattern(self, task: AutomationTask) -> str:
        """Extract pattern from task."""
        return f"{task.task_type}_{len(task.parameters)}"


class OptimizationEngine:
    """Optimization engine for automation."""
    
    def __init__(self):
        self.optimization_strategies = [
            self._optimize_worker_count,
            self._optimize_task_priorities,
            self._optimize_resource_usage
        ]
    
    def optimize(self, metrics: PerformanceMetrics, tasks: Dict[str, AutomationTask]) -> Dict[str, Any]:
        """Optimize automation performance."""
        optimizations = {}
        
        for strategy in self.optimization_strategies:
            result = strategy(metrics, tasks)
            if result:
                optimizations.update(result)
        
        return optimizations
    
    def _optimize_worker_count(self, metrics: PerformanceMetrics, tasks: Dict[str, AutomationTask]) -> Dict[str, Any]:
        """Optimize worker count based on performance."""
        if metrics.throughput < 1.0:  # Less than 1 task per minute
            return {"suggestion": "Increase worker count", "reason": "Low throughput"}
        return {}
    
    def _optimize_task_priorities(self, metrics: PerformanceMetrics, tasks: Dict[str, AutomationTask]) -> Dict[str, Any]:
        """Optimize task priorities."""
        if metrics.error_rate > 0.3:  # More than 30% error rate
            return {"suggestion": "Review task priorities", "reason": "High error rate"}
        return {}
    
    def _optimize_resource_usage(self, metrics: PerformanceMetrics, tasks: Dict[str, AutomationTask]) -> Dict[str, Any]:
        """Optimize resource usage."""
        if metrics.average_duration > 60:  # Average task takes more than 1 minute
            return {"suggestion": "Optimize task execution", "reason": "Long average duration"}
        return {}
