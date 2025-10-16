"""
Advanced Safety Controller for comprehensive security and permission management.

This module provides extensive safety controls including:
- Permission-based access control
- Resource usage monitoring
- Security policy enforcement
- Audit logging and compliance
- Risk assessment and mitigation
- Emergency stop mechanisms
- Data protection and privacy controls
"""

import os
import json
import time
import logging
import hashlib
import threading
from typing import Optional, Dict, List, Any, Union, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class PermissionLevel(Enum):
    """Permission levels for different operations."""
    FULL_ACCESS = "full_access"  # Allows full editing, creation, and modification capabilities
    LIMITED = "limited"
    STANDARD = "standard"
    ELEVATED = "elevated"
    ADMIN = "admin"


class RiskLevel(Enum):
    """Risk levels for operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    name: str
    description: str
    allowed_actions: Set[str]
    blocked_actions: Set[str]
    allowed_domains: Set[str]
    blocked_domains: Set[str]
    allowed_paths: Set[str]
    blocked_paths: Set[str]
    max_file_size: int
    max_operations_per_minute: int
    max_concurrent_operations: int
    require_approval: bool
    risk_threshold: RiskLevel


@dataclass
class OperationContext:
    """Context for a security operation."""
    operation_id: str
    user_id: str
    action: str
    resource: str
    timestamp: datetime
    risk_level: RiskLevel
    requires_approval: bool
    approved: bool = False
    approval_timestamp: Optional[datetime] = None
    approver_id: Optional[str] = None


class SecurityAuditLogger:
    """Comprehensive security audit logging."""
    
    def __init__(self, log_file: str = "security_audit.log"):
        self.log_file = log_file
        self.log_lock = threading.Lock()
        self.audit_entries = []
        self.max_entries = 10000
    
    def log_operation(self, context: OperationContext, success: bool, 
                     details: Dict[str, Any] = None):
        """Log a security operation."""
        entry = {
            "timestamp": context.timestamp.isoformat(),
            "operation_id": context.operation_id,
            "user_id": context.user_id,
            "action": context.action,
            "resource": context.resource,
            "risk_level": context.risk_level.value,
            "success": success,
            "requires_approval": context.requires_approval,
            "approved": context.approved,
            "approver_id": context.approver_id,
            "details": details or {}
        }
        
        with self.log_lock:
            self.audit_entries.append(entry)
            
            # Keep only recent entries
            if len(self.audit_entries) > self.max_entries:
                self.audit_entries = self.audit_entries[-self.max_entries:]
            
            # Write to file
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry) + "\n")
            except Exception as e:
                logging.error(f"Failed to write audit log: {e}")
    
    def get_audit_trail(self, user_id: Optional[str] = None, 
                       action: Optional[str] = None,
                       start_time: Optional[datetime] = None,
                       end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Get audit trail with optional filters."""
        with self.log_lock:
            entries = self.audit_entries.copy()
        
        # Apply filters
        if user_id:
            entries = [e for e in entries if e["user_id"] == user_id]
        if action:
            entries = [e for e in entries if e["action"] == action]
        if start_time:
            entries = [e for e in entries if datetime.fromisoformat(e["timestamp"]) >= start_time]
        if end_time:
            entries = [e for e in entries if datetime.fromisoformat(e["timestamp"]) <= end_time]
        
        return entries


class AdvancedSafetyController:
    """Advanced safety and security controller."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "safety_config.json"
        self.policies = {}
        self.active_policy = None
        self.operation_contexts = {}
        self.pending_approvals = {}
        self.emergency_stop = False
        
        # Resource monitoring
        self.resource_usage = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_usage": 0.0,
            "network_io": 0
        }
        self.resource_monitor_thread = None
        self.monitoring_active = False
        
        # Audit logging
        self.audit_logger = SecurityAuditLogger()
        
        # Safety controls
        self.max_risk_operations = 10
        self.risk_operation_count = 0
        self.risk_window_start = time.time()

        # Download monitoring
        self.download_directories = self._get_download_directories()
        self.download_monitor_thread = None
        self.monitoring_downloads = False
        self.known_files = self._scan_existing_files()

        # Load configuration
        self._load_configuration()

        # Start resource monitoring
        self._start_resource_monitoring()

        # Start download monitoring
        self._start_download_monitoring()
    
    def _load_configuration(self):
        """Load safety configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # Load policies
                for policy_data in config.get("policies", []):
                    policy = SecurityPolicy(
                        name=policy_data["name"],
                        description=policy_data["description"],
                        allowed_actions=set(policy_data.get("allowed_actions", [])),
                        blocked_actions=set(policy_data.get("blocked_actions", [])),
                        allowed_domains=set(policy_data.get("allowed_domains", [])),
                        blocked_domains=set(policy_data.get("blocked_domains", [])),
                        allowed_paths=set(policy_data.get("allowed_paths", [])),
                        blocked_paths=set(policy_data.get("blocked_paths", [])),
                        max_file_size=policy_data.get("max_file_size", 100 * 1024 * 1024),
                        max_operations_per_minute=policy_data.get("max_operations_per_minute", 100),
                        max_concurrent_operations=policy_data.get("max_concurrent_operations", 10),
                        require_approval=policy_data.get("require_approval", False),
                        risk_threshold=RiskLevel(policy_data.get("risk_threshold", "medium"))
                    )
                    self.policies[policy.name] = policy
                
                # Set active policy
                active_policy_name = config.get("active_policy")
                if active_policy_name and active_policy_name in self.policies:
                    self.active_policy = self.policies[active_policy_name]
        except Exception as e:
            logging.error(f"Failed to load safety configuration: {e}")
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default safety configuration."""
        # System directories to block (except Startup directory)
        system_blocked_paths = {
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\System32",
            "C:\\Temp",
            "C:\\Windows\\System32"
        }

        default_policy = SecurityPolicy(
            name="default",
            description="Default safety policy",
            allowed_actions=set(),
            blocked_actions=set(),
            allowed_domains=set(),
            blocked_domains={"malicious-site.com", "phishing-site.com"},
            allowed_paths=set(),
            blocked_paths=system_blocked_paths,
            max_file_size=5 * 1024 * 1024 * 1024,  # 5GB
            max_operations_per_minute=50,
            max_concurrent_operations=5,
            require_approval=False,
            risk_threshold=RiskLevel.CRITICAL
        )
        
        self.policies["default"] = default_policy
        self.active_policy = default_policy
        self._save_configuration()
    
    def _save_configuration(self):
        """Save safety configuration to file."""
        try:
            config = {
                "active_policy": self.active_policy.name if self.active_policy else None,
                "policies": [
                    {
                        "name": policy.name,
                        "description": policy.description,
                        "allowed_actions": list(policy.allowed_actions),
                        "blocked_actions": list(policy.blocked_actions),
                        "allowed_domains": list(policy.allowed_domains),
                        "blocked_domains": list(policy.blocked_domains),
                        "allowed_paths": list(policy.allowed_paths),
                        "blocked_paths": list(policy.blocked_paths),
                        "max_file_size": policy.max_file_size,
                        "max_operations_per_minute": policy.max_operations_per_minute,
                        "max_concurrent_operations": policy.max_concurrent_operations,
                        "require_approval": policy.require_approval,
                        "risk_threshold": policy.risk_threshold.value
                    }
                    for policy in self.policies.values()
                ]
            }
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save safety configuration: {e}")
    
    def _start_resource_monitoring(self):
        """Start resource usage monitoring."""
        if not PSUTIL_AVAILABLE:
            logging.warning("psutil not available, resource monitoring disabled")
            return
        
        self.monitoring_active = True
        self.resource_monitor_thread = threading.Thread(target=self._monitor_resources)
        self.resource_monitor_thread.daemon = True
        self.resource_monitor_thread.start()
    
    def _monitor_resources(self):
        """Monitor system resource usage."""
        while self.monitoring_active:
            try:
                if PSUTIL_AVAILABLE:
                    self.resource_usage["cpu_percent"] = psutil.cpu_percent()
                    self.resource_usage["memory_percent"] = psutil.virtual_memory().percent
                    self.resource_usage["disk_usage"] = psutil.disk_usage('/').percent
                    
                    # Check for resource limits
                    if self.resource_usage["cpu_percent"] > 90:
                        logging.warning("High CPU usage detected")
                    if self.resource_usage["memory_percent"] > 90:
                        logging.warning("High memory usage detected")
                        self._trigger_emergency_stop("High memory usage")
                
                time.sleep(5)  # Monitor every 5 seconds
            except Exception as e:
                logging.error(f"Resource monitoring error: {e}")
                time.sleep(10)
    
    def _trigger_emergency_stop(self, reason: str):
        """Trigger emergency stop for safety."""
        self.emergency_stop = True
        logging.critical(f"EMERGENCY STOP TRIGGERED: {reason}")
        
        # Log emergency stop
        context = OperationContext(
            operation_id=str(uuid.uuid4()),
            user_id="system",
            action="emergency_stop",
            resource="system",
            timestamp=datetime.now(),
            risk_level=RiskLevel.CRITICAL,
            requires_approval=False
        )
        self.audit_logger.log_operation(context, True, {"reason": reason})
    
    def check_permission(self, user_id: str, action: str, resource: str, user_permission_level: Optional[PermissionLevel] = None) -> Tuple[bool, str]:
        """Check if user has permission for an action."""
        if self.emergency_stop:
            return False, "Emergency stop active"

        if not self.active_policy:
            return False, "No active security policy"

        # FULL_ACCESS level gets unrestricted permissions for all operations
        if user_permission_level == PermissionLevel.FULL_ACCESS:
            return True, "Full access permission granted"

        # Check blocked actions
        if self.active_policy.blocked_actions and action in self.active_policy.blocked_actions:
            return False, f"Action '{action}' is blocked by policy"

        # Check allowed actions (if specified)
        if self.active_policy.allowed_actions and action not in self.active_policy.allowed_actions:
            return False, f"Action '{action}' not in allowed actions"

        # Check domain restrictions for web resources
        if resource.startswith("http"):
            from urllib.parse import urlparse
            domain = urlparse(resource).netloc.lower()

            if self.active_policy.blocked_domains and any(blocked in domain for blocked in self.active_policy.blocked_domains):
                return False, f"Domain '{domain}' is blocked by policy"

            if self.active_policy.allowed_domains and not any(allowed in domain for allowed in self.active_policy.allowed_domains):
                return False, f"Domain '{domain}' not in allowed domains"

        # Check path restrictions for file resources
        if resource.startswith("/") or "\\" in resource:
            resource_path = os.path.abspath(resource)

            if self.active_policy.blocked_paths and any(resource_path.startswith(blocked) for blocked in self.active_policy.blocked_paths):
                return False, f"Path '{resource_path}' is blocked by policy"

            if self.active_policy.allowed_paths and not any(resource_path.startswith(allowed) for allowed in self.active_policy.allowed_paths):
                return False, f"Path '{resource_path}' not in allowed paths"

        return True, "Permission granted"
    
    def assess_risk(self, action: str, resource: str, context: Dict[str, Any] = None) -> RiskLevel:
        """Assess risk level of an operation."""
        risk_factors = []
        
        # High-risk actions
        high_risk_actions = {"delete", "format", "shutdown", "restart", "execute", "install"}
        if action in high_risk_actions:
            risk_factors.append("high_risk_action")
        
        # System resources
        if resource.startswith("/system") or resource.startswith("C:\\Windows"):
            risk_factors.append("system_resource")
        
        # Network resources
        if resource.startswith("http"):
            risk_factors.append("network_resource")
        
        # File size considerations
        if context and "file_size" in context:
            if context["file_size"] > 100 * 1024 * 1024:  # 100MB
                risk_factors.append("large_file")
        
        # Determine risk level
        if len(risk_factors) >= 3 or "system_resource" in risk_factors:
            return RiskLevel.CRITICAL
        elif len(risk_factors) >= 2 or "high_risk_action" in risk_factors:
            return RiskLevel.HIGH
        elif len(risk_factors) >= 1:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def request_operation(self, user_id: str, action: str, resource: str,
                          context: Dict[str, Any] = None, user_permission_level: Optional[PermissionLevel] = None) -> Tuple[bool, str, Optional[str]]:
        """Request permission for an operation."""
        # Check basic permission
        has_permission, message = self.check_permission(user_id, action, resource, user_permission_level)
        if not has_permission:
            return False, message, None

        # Assess risk
        risk_level = self.assess_risk(action, resource, context)

        # Determine if approval is required
        requires_approval = self.active_policy.require_approval

        # Prompt user for high/critical risk operations
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            print(f"WARNING: Operation '{action}' on '{resource}' has {risk_level.value.upper()} risk level.")
            print("This operation may be dangerous. Do you want to proceed?")
            try:
                confirm = input("Proceed with dangerous action? (y/N): ").lower().strip()
                if confirm != 'y':
                    return False, "Operation cancelled by user due to high risk", None
            except (EOFError, KeyboardInterrupt):
                return False, "Operation cancelled", None
            # If user confirms, require approval for high/critical operations
            requires_approval = True

        # Create operation context
        operation_id = str(uuid.uuid4())
        operation_context = OperationContext(
            operation_id=operation_id,
            user_id=user_id,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            risk_level=risk_level,
            requires_approval=requires_approval
        )

        # Check if approval is required
        if operation_context.requires_approval:
            self.pending_approvals[operation_id] = operation_context
            return False, f"Operation requires approval (Risk: {risk_level.value})", operation_id

        # Check risk limits
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            current_time = time.time()
            if current_time - self.risk_window_start > 3600:  # 1 hour window
                self.risk_operation_count = 0
                self.risk_window_start = current_time

            if self.risk_operation_count >= self.max_risk_operations:
                return False, "Risk operation limit exceeded", None

            self.risk_operation_count += 1

        # Store operation context
        self.operation_contexts[operation_id] = operation_context

        # Log operation
        self.audit_logger.log_operation(operation_context, True, context)

        return True, "Operation approved", operation_id
    
    def approve_operation(self, operation_id: str, approver_id: str) -> bool:
        """Approve a pending operation."""
        if operation_id not in self.pending_approvals:
            return False
        
        operation_context = self.pending_approvals[operation_id]
        operation_context.approved = True
        operation_context.approval_timestamp = datetime.now()
        operation_context.approver_id = approver_id
        
        # Move to active operations
        self.operation_contexts[operation_id] = operation_context
        del self.pending_approvals[operation_id]
        
        # Log approval
        self.audit_logger.log_operation(operation_context, True, {"approver": approver_id})
        
        return True
    
    def deny_operation(self, operation_id: str, approver_id: str, reason: str) -> bool:
        """Deny a pending operation."""
        if operation_id not in self.pending_approvals:
            return False
        
        operation_context = self.pending_approvals[operation_id]
        operation_context.approved = False
        operation_context.approval_timestamp = datetime.now()
        operation_context.approver_id = approver_id
        
        # Log denial
        self.audit_logger.log_operation(operation_context, False, 
                                      {"approver": approver_id, "reason": reason})
        
        del self.pending_approvals[operation_id]
        return True
    
    def complete_operation(self, operation_id: str, success: bool, 
                          details: Dict[str, Any] = None):
        """Mark an operation as completed."""
        if operation_id in self.operation_contexts:
            operation_context = self.operation_contexts[operation_id]
            self.audit_logger.log_operation(operation_context, success, details)
            del self.operation_contexts[operation_id]
    
    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Get list of pending approvals."""
        return [
            {
                "operation_id": context.operation_id,
                "user_id": context.user_id,
                "action": context.action,
                "resource": context.resource,
                "risk_level": context.risk_level.value,
                "timestamp": context.timestamp.isoformat()
            }
            for context in self.pending_approvals.values()
        ]
    
    def get_active_operations(self) -> List[Dict[str, Any]]:
        """Get list of active operations."""
        return [
            {
                "operation_id": context.operation_id,
                "user_id": context.user_id,
                "action": context.action,
                "resource": context.resource,
                "risk_level": context.risk_level.value,
                "timestamp": context.timestamp.isoformat(),
                "approved": context.approved
            }
            for context in self.operation_contexts.values()
        ]
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        return self.resource_usage.copy()
    
    def get_audit_trail(self, **kwargs) -> List[Dict[str, Any]]:
        """Get security audit trail."""
        return self.audit_logger.get_audit_trail(**kwargs)
    
    def set_policy(self, policy_name: str) -> bool:
        """Set active security policy."""
        if policy_name not in self.policies:
            return False
        
        self.active_policy = self.policies[policy_name]
        self._save_configuration()
        return True
    
    def create_policy(self, policy: SecurityPolicy) -> bool:
        """Create a new security policy."""
        try:
            self.policies[policy.name] = policy
            self._save_configuration()
            return True
        except Exception as e:
            logging.error(f"Failed to create policy: {e}")
            return False
    
    def update_policy(self, policy_name: str, **updates) -> bool:
        """Update an existing security policy."""
        if policy_name not in self.policies:
            return False
        
        try:
            policy = self.policies[policy_name]
            for key, value in updates.items():
                if hasattr(policy, key):
                    setattr(policy, key, value)
            
            self._save_configuration()
            return True
        except Exception as e:
            logging.error(f"Failed to update policy: {e}")
            return False
    
    def emergency_stop(self, reason: str = "Manual emergency stop"):
        """Manually trigger emergency stop."""
        self._trigger_emergency_stop(reason)
    
    def emergency_resume(self):
        """Resume operations after emergency stop."""
        self.emergency_stop = False
        logging.info("Emergency stop cleared, operations resumed")
    
    def get_safety_status(self) -> Dict[str, Any]:
        """Get comprehensive safety status."""
        return {
            "emergency_stop": self.emergency_stop,
            "active_policy": self.active_policy.name if self.active_policy else None,
            "pending_approvals": len(self.pending_approvals),
            "active_operations": len(self.operation_contexts),
            "resource_usage": self.resource_usage,
            "risk_operation_count": self.risk_operation_count,
            "max_risk_operations": self.max_risk_operations
        }
    
    def _get_download_directories(self) -> List[str]:
        """Get common download directory paths."""
        download_dirs = []

        # Default download directories
        if os.name == 'nt':  # Windows
            download_dirs.extend([
                str(Path.home() / "Downloads"),
                str(Path.home() / "Desktop"),
                os.environ.get('TEMP', 'C:\\Temp'),
                os.environ.get('TMP', 'C:\\Tmp')
            ])
        else:  # Unix-like systems
            download_dirs.extend([
                str(Path.home() / "Downloads"),
                str(Path.home() / "Desktop"),
                "/tmp",
                "/var/tmp"
            ])

        # Add current working directory
        download_dirs.append(os.getcwd())

        # Filter to existing directories
        return [d for d in download_dirs if os.path.exists(d)]

    def _scan_existing_files(self) -> Dict[str, Set[str]]:
        """Scan existing files in download directories."""
        known_files = {}
        for directory in self.download_directories:
            try:
                files = set()
                for root, _, filenames in os.walk(directory):
                    for filename in filenames:
                        files.add(os.path.join(root, filename))
                known_files[directory] = files
            except Exception as e:
                logging.warning(f"Failed to scan directory {directory}: {e}")
                known_files[directory] = set()
        return known_files

    def _start_download_monitoring(self):
        """Start monitoring for automatic file downloads."""
        if not self.download_directories:
            logging.warning("No download directories found, download monitoring disabled")
            return

        self.monitoring_downloads = True
        self.download_monitor_thread = threading.Thread(target=self._monitor_downloads)
        self.download_monitor_thread.daemon = True
        self.download_monitor_thread.start()

    def _monitor_downloads(self):
        """Monitor download directories for new files."""
        while self.monitoring_downloads:
            try:
                for directory in self.download_directories:
                    current_files = set()
                    try:
                        for root, _, filenames in os.walk(directory):
                            for filename in filenames:
                                current_files.add(os.path.join(root, filename))
                    except Exception:
                        continue

                    # Find new files
                    previous_files = self.known_files.get(directory, set())
                    new_files = current_files - previous_files

                    # Inspect new files
                    for file_path in new_files:
                        try:
                            # Check if file is recently created (within last 30 seconds)
                            if os.path.exists(file_path):
                                mtime = os.path.getmtime(file_path)
                                if time.time() - mtime < 30:  # New file
                                    self.inspect_downloaded_file(file_path)
                        except Exception as e:
                            logging.error(f"Error checking new file {file_path}: {e}")

                    # Update known files
                    self.known_files[directory] = current_files

                time.sleep(5)  # Check every 5 seconds

            except Exception as e:
                logging.error(f"Download monitoring error: {e}")
                time.sleep(10)

    def inspect_downloaded_file(self, file_path: str) -> Tuple[bool, str]:
        """Inspect a downloaded file for dangerous content and auto-delete if malicious."""
        try:
            if not os.path.exists(file_path):
                return True, "File does not exist"

            # Get file info
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path).lower()

            # Dangerous file extensions
            dangerous_extensions = {
                '.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js',
                '.jar', '.msi', '.dll', '.sys', '.drv', '.ocx', '.cpl'
            }

            # Check file extension
            _, ext = os.path.splitext(file_name)
            if ext in dangerous_extensions:
                os.remove(file_path)
                return False, f"Deleted dangerous file: {file_name} (executable extension)"

            # Check file size (suspiciously large files)
            if file_size > 100 * 1024 * 1024:  # 100MB
                os.remove(file_path)
                return False, f"Deleted suspicious large file: {file_name} ({file_size} bytes)"

            # Check for suspicious content patterns
            try:
                with open(file_path, 'rb') as f:
                    content = f.read(1024)  # Read first 1KB

                    # Check for executable signatures
                    if content.startswith(b'MZ'):  # Windows executable
                        os.remove(file_path)
                        return False, f"Deleted executable file: {file_name}"

                    if content.startswith(b'#!/'):  # Script file
                        os.remove(file_path)
                        return False, f"Deleted script file: {file_name}"

                    # Check for suspicious strings
                    suspicious_patterns = [b'virus', b'malware', b'trojan', b'ransomware']
                    content_str = content.decode('utf-8', errors='ignore').lower()
                    for pattern in suspicious_patterns:
                        if pattern.decode() in content_str:
                            os.remove(file_path)
                            return False, f"Deleted file containing suspicious content: {file_name}"

            except Exception as e:
                # Gracefully skip locked files (common on Windows: WinError 32)
                if isinstance(e, PermissionError) or getattr(e, 'winerror', None) == 32:
                    return True, f"Skipped locked file: {file_name}"
                # If we can't read the file for other reasons, consider it suspicious
                os.remove(file_path)
                return False, f"Deleted unreadable file: {file_name} ({str(e)})"

            return True, f"File {file_name} passed inspection"

        except Exception as e:
            # If the file is locked, skip without error
            if isinstance(e, PermissionError) or getattr(e, 'winerror', None) == 32:
                logging.debug(f"Skipped locked file during inspection: {file_path}")
                return True, f"Skipped locked file: {os.path.basename(file_path)}"
            logging.error(f"File inspection error for {file_path}: {e}")
            return False, f"Inspection failed: {str(e)}"

    def cleanup(self):
        """Clean up resources and stop monitoring."""
        self.monitoring_active = False
        self.monitoring_downloads = False
        if self.resource_monitor_thread:
            self.resource_monitor_thread.join(timeout=5)
        if self.download_monitor_thread:
            self.download_monitor_thread.join(timeout=5)
