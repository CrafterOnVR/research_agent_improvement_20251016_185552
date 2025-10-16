"""
Advanced File System Controller for comprehensive file and directory management.

This module provides extensive file system control capabilities including:
- Advanced file operations (copy, move, delete, search, replace)
- Directory management and batch operations
- File watching and monitoring
- Content analysis and processing
- Backup and synchronization
- File compression and archiving
- Pattern matching and filtering
"""

import os
import shutil
import time
import hashlib
import logging
import threading
import zipfile
import tarfile
import json
import csv
from typing import Optional, Dict, List, Any, Union, Callable, Tuple, Iterator
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import fnmatch
import re

try:
    import watchdog
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class FileWatcher(FileSystemEventHandler):
    """File system event handler for monitoring changes."""
    
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback
        self.last_events = {}
        self.debounce_time = 1.0  # seconds
    
    def on_modified(self, event):
        if not event.is_directory:
            self._debounce_event(event.src_path, "modified")
    
    def on_created(self, event):
        if not event.is_directory:
            self._debounce_event(event.src_path, "created")
    
    def on_deleted(self, event):
        if not event.is_directory:
            self._debounce_event(event.src_path, "deleted")
    
    def on_moved(self, event):
        if not event.is_directory:
            self._debounce_event(event.dest_path, "moved")
    
    def _debounce_event(self, path: str, event_type: str):
        """Debounce events to avoid rapid-fire callbacks."""
        current_time = time.time()
        key = f"{path}:{event_type}"
        
        if key in self.last_events:
            if current_time - self.last_events[key] < self.debounce_time:
                return
        
        self.last_events[key] = current_time
        self.callback(path, event_type)


class AdvancedFileController:
    """Advanced file system automation with comprehensive control capabilities."""
    
    def __init__(self, base_path: str = ".", enable_watching: bool = False):
        self.base_path = Path(base_path).resolve()
        self.enable_watching = enable_watching and WATCHDOG_AVAILABLE
        self.observer = None
        self.watcher = None
        self.watch_callbacks = []
        
        # Safety controls
        self.allowed_paths = set()
        self.blocked_paths = set()
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.operation_count = 0
        self.operation_window_start = time.time()
        self.max_operations_per_minute = 100
        
        # File operation history
        self.operation_history = []
        self.backup_dir = self.base_path / ".backups"
        self.backup_dir.mkdir(exist_ok=True)
    
    def start_watching(self, callback: Optional[Callable[[str, str], None]] = None):
        """Start file system watching."""
        if not self.enable_watching:
            logging.warning("File watching not available (watchdog not installed)")
            return False
        
        if callback:
            self.watch_callbacks.append(callback)
        
        try:
            self.watcher = FileWatcher(self._handle_file_event)
            self.observer = Observer()
            self.observer.schedule(self.watcher, str(self.base_path), recursive=True)
            self.observer.start()
            return True
        except Exception as e:
            logging.error(f"Failed to start file watching: {e}")
            return False
    
    def stop_watching(self):
        """Stop file system watching."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
    
    def _handle_file_event(self, path: str, event_type: str):
        """Handle file system events."""
        for callback in self.watch_callbacks:
            try:
                callback(path, event_type)
            except Exception as e:
                logging.error(f"File event callback error: {e}")
    
    def _check_path_safety(self, path: Union[str, Path]) -> bool:
        """Check if path is safe to operate on."""
        path = Path(path).resolve()
        
        # Check if path is within allowed paths
        if self.allowed_paths:
            if not any(path.is_relative_to(allowed) for allowed in self.allowed_paths):
                return False
        
        # Check if path is in blocked paths
        if self.blocked_paths:
            if any(path.is_relative_to(blocked) for blocked in self.blocked_paths):
                return False
        
        return True
    
    def _enforce_rate_limit(self):
        """Enforce operation rate limiting."""
        current_time = time.time()
        
        if current_time - self.operation_window_start > 60:
            self.operation_count = 0
            self.operation_window_start = current_time
        
        if self.operation_count >= self.max_operations_per_minute:
            sleep_time = 60 - (current_time - self.operation_window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.operation_count = 0
                self.operation_window_start = time.time()
        
        self.operation_count += 1
    
    def _log_operation(self, operation: str, source: str, destination: str = None, 
                      success: bool = True, error: str = None):
        """Log file operations for audit trail."""
        self.operation_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "source": str(source),
            "destination": str(destination) if destination else None,
            "success": success,
            "error": error
        })
        
        # Keep only last 1000 operations
        if len(self.operation_history) > 1000:
            self.operation_history = self.operation_history[-1000:]
    
    def create_file(self, path: str, content: str = "", encoding: str = "utf-8") -> bool:
        """Create a file with content."""
        if not self._check_path_safety(path):
            return False
        
        self._enforce_rate_limit()
        
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            
            self._log_operation("create_file", path, success=True)
            return True
        except Exception as e:
            self._log_operation("create_file", path, success=False, error=str(e))
            logging.error(f"File creation failed: {e}")
            return False
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Optional[str]:
        """Read file content."""
        if not self._check_path_safety(path):
            return None
        
        try:
            file_path = Path(path)
            if not file_path.exists():
                return None
            
            # Check file size
            if file_path.stat().st_size > self.max_file_size:
                logging.warning(f"File too large: {path}")
                return None
            
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            logging.error(f"File read failed: {e}")
            return None
    
    def write_file(self, path: str, content: str, encoding: str = "utf-8", 
                  backup: bool = True) -> bool:
        """Write content to a file."""
        if not self._check_path_safety(path):
            return False
        
        self._enforce_rate_limit()
        
        try:
            file_path = Path(path)
            
            # Create backup if file exists and backup is enabled
            if file_path.exists() and backup:
                self._create_backup(file_path)
            
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            
            self._log_operation("write_file", path, success=True)
            return True
        except Exception as e:
            self._log_operation("write_file", path, success=False, error=str(e))
            logging.error(f"File write failed: {e}")
            return False
    
    def copy_file(self, source: str, destination: str, preserve_metadata: bool = True) -> bool:
        """Copy a file."""
        if not self._check_path_safety(source) or not self._check_path_safety(destination):
            return False
        
        self._enforce_rate_limit()
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if preserve_metadata:
                shutil.copy2(source_path, dest_path)
            else:
                shutil.copy(source_path, dest_path)
            
            self._log_operation("copy_file", source, destination, success=True)
            return True
        except Exception as e:
            self._log_operation("copy_file", source, destination, success=False, error=str(e))
            logging.error(f"File copy failed: {e}")
            return False
    
    def move_file(self, source: str, destination: str) -> bool:
        """Move a file."""
        if not self._check_path_safety(source) or not self._check_path_safety(destination):
            return False
        
        self._enforce_rate_limit()
        
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if not source_path.exists():
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source_path), str(dest_path))
            
            self._log_operation("move_file", source, destination, success=True)
            return True
        except Exception as e:
            self._log_operation("move_file", source, destination, success=False, error=str(e))
            logging.error(f"File move failed: {e}")
            return False
    
    def delete_file(self, path: str, backup: bool = True) -> bool:
        """Delete a file."""
        if not self._check_path_safety(path):
            return False
        
        self._enforce_rate_limit()
        
        try:
            file_path = Path(path)
            
            if not file_path.exists():
                return True  # Already deleted
            
            # Create backup if enabled
            if backup:
                self._create_backup(file_path)
            
            file_path.unlink()
            
            self._log_operation("delete_file", path, success=True)
            return True
        except Exception as e:
            self._log_operation("delete_file", path, success=False, error=str(e))
            logging.error(f"File deletion failed: {e}")
            return False
    
    def create_directory(self, path: str, parents: bool = True) -> bool:
        """Create a directory."""
        if not self._check_path_safety(path):
            return False
        
        self._enforce_rate_limit()
        
        try:
            dir_path = Path(path)
            dir_path.mkdir(parents=parents, exist_ok=True)
            
            self._log_operation("create_directory", path, success=True)
            return True
        except Exception as e:
            self._log_operation("create_directory", path, success=False, error=str(e))
            logging.error(f"Directory creation failed: {e}")
            return False
    
    def delete_directory(self, path: str, recursive: bool = True) -> bool:
        """Delete a directory."""
        if not self._check_path_safety(path):
            return False
        
        self._enforce_rate_limit()
        
        try:
            dir_path = Path(path)
            
            if not dir_path.exists():
                return True  # Already deleted
            
            if recursive:
                shutil.rmtree(dir_path)
            else:
                dir_path.rmdir()
            
            self._log_operation("delete_directory", path, success=True)
            return True
        except Exception as e:
            self._log_operation("delete_directory", path, success=False, error=str(e))
            logging.error(f"Directory deletion failed: {e}")
            return False
    
    def find_files(self, pattern: str, directory: str = None, 
                  recursive: bool = True) -> List[str]:
        """Find files matching a pattern."""
        search_dir = Path(directory) if directory else self.base_path
        
        if not self._check_path_safety(search_dir):
            return []
        
        try:
            files = []
            if recursive:
                for file_path in search_dir.rglob(pattern):
                    if file_path.is_file() and self._check_path_safety(file_path):
                        files.append(str(file_path))
            else:
                for file_path in search_dir.glob(pattern):
                    if file_path.is_file() and self._check_path_safety(file_path):
                        files.append(str(file_path))
            
            return files
        except Exception as e:
            logging.error(f"File search failed: {e}")
            return []
    
    def search_content(self, pattern: str, directory: str = None, 
                      file_pattern: str = "*", case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for content in files."""
        search_dir = Path(directory) if directory else self.base_path
        
        if not self._check_path_safety(search_dir):
            return []
        
        try:
            results = []
            files = self.find_files(file_pattern, str(search_dir))
            
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            for file_path in files:
                try:
                    content = self.read_file(file_path)
                    if content:
                        matches = list(regex.finditer(content))
                        if matches:
                            results.append({
                                "file": file_path,
                                "matches": [
                                    {
                                        "line": content[:match.start()].count('\n') + 1,
                                        "text": match.group(),
                                        "start": match.start(),
                                        "end": match.end()
                                    }
                                    for match in matches
                                ]
                            })
                except Exception as e:
                    logging.warning(f"Error searching in {file_path}: {e}")
                    continue
            
            return results
        except Exception as e:
            logging.error(f"Content search failed: {e}")
            return []
    
    def replace_content(self, pattern: str, replacement: str, directory: str = None,
                       file_pattern: str = "*", case_sensitive: bool = False) -> int:
        """Replace content in files."""
        search_dir = Path(directory) if directory else self.base_path
        
        if not self._check_path_safety(search_dir):
            return 0
        
        try:
            files = self.find_files(file_pattern, str(search_dir))
            replaced_count = 0
            
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
            
            for file_path in files:
                try:
                    content = self.read_file(file_path)
                    if content:
                        new_content = regex.sub(replacement, content)
                        if new_content != content:
                            self.write_file(file_path, new_content)
                            replaced_count += 1
                except Exception as e:
                    logging.warning(f"Error replacing in {file_path}: {e}")
                    continue
            
            return replaced_count
        except Exception as e:
            logging.error(f"Content replacement failed: {e}")
            return 0
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive file information."""
        if not self._check_path_safety(path):
            return None
        
        try:
            file_path = Path(path)
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "is_symlink": file_path.is_symlink(),
                "permissions": oct(stat.st_mode)[-3:],
                "hash": self._calculate_hash(file_path)
            }
        except Exception as e:
            logging.error(f"Failed to get file info: {e}")
            return None
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""
    
    def _create_backup(self, file_path: Path):
        """Create a backup of a file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}.{timestamp}.bak"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
        except Exception as e:
            logging.warning(f"Backup creation failed: {e}")
    
    def create_archive(self, source_dir: str, archive_path: str, 
                      format: str = "zip") -> bool:
        """Create an archive from a directory."""
        if not self._check_path_safety(source_dir) or not self._check_path_safety(archive_path):
            return False
        
        try:
            source_path = Path(source_dir)
            archive_path = Path(archive_path)
            
            if format.lower() == "zip":
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in source_path.rglob("*"):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source_path)
                            zipf.write(file_path, arcname)
            elif format.lower() == "tar":
                with tarfile.open(archive_path, 'w') as tar:
                    tar.add(source_path, arcname=source_path.name)
            else:
                raise ValueError(f"Unsupported archive format: {format}")
            
            return True
        except Exception as e:
            logging.error(f"Archive creation failed: {e}")
            return False
    
    def extract_archive(self, archive_path: str, destination: str) -> bool:
        """Extract an archive."""
        if not self._check_path_safety(archive_path) or not self._check_path_safety(destination):
            return False
        
        try:
            archive_path = Path(archive_path)
            dest_path = Path(destination)
            
            dest_path.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix.lower() == ".zip":
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    zipf.extractall(dest_path)
            elif archive_path.suffix.lower() in [".tar", ".tar.gz", ".tgz"]:
                with tarfile.open(archive_path, 'r') as tar:
                    tar.extractall(dest_path)
            else:
                raise ValueError(f"Unsupported archive format: {archive_path.suffix}")
            
            return True
        except Exception as e:
            logging.error(f"Archive extraction failed: {e}")
            return False
    
    def get_directory_tree(self, directory: str = None, max_depth: int = 5) -> Dict[str, Any]:
        """Get directory tree structure."""
        search_dir = Path(directory) if directory else self.base_path
        
        if not self._check_path_safety(search_dir):
            return {}
        
        def build_tree(path: Path, current_depth: int = 0):
            if current_depth >= max_depth:
                return {"type": "truncated", "name": "..."}
            
            if path.is_file():
                return {
                    "type": "file",
                    "name": path.name,
                    "size": path.stat().st_size
                }
            elif path.is_dir():
                children = []
                try:
                    for child in sorted(path.iterdir()):
                        if self._check_path_safety(child):
                            children.append(build_tree(child, current_depth + 1))
                except PermissionError:
                    children = [{"type": "error", "name": "Permission denied"}]
                
                return {
                    "type": "directory",
                    "name": path.name,
                    "children": children
                }
            else:
                return {"type": "unknown", "name": path.name}
        
        return build_tree(search_dir)
    
    def set_safety_controls(self, allowed_paths: List[str] = None,
                           blocked_paths: List[str] = None,
                           max_file_size: int = None,
                           max_operations_per_minute: int = None):
        """Configure safety controls."""
        if allowed_paths:
            self.allowed_paths = {Path(p).resolve() for p in allowed_paths}
        if blocked_paths:
            self.blocked_paths = {Path(p).resolve() for p in blocked_paths}
        if max_file_size:
            self.max_file_size = max_file_size
        if max_operations_per_minute:
            self.max_operations_per_minute = max_operations_per_minute
    
    def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get operation history."""
        return self.operation_history[-limit:] if limit else self.operation_history
    
    def cleanup_backups(self, older_than_days: int = 30):
        """Clean up old backup files."""
        try:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*.bak"):
                if backup_file.stat().st_mtime < cutoff_time.timestamp():
                    backup_file.unlink()
                    deleted_count += 1
            
            return deleted_count
        except Exception as e:
            logging.error(f"Backup cleanup failed: {e}")
            return 0
