"""
Advanced GitHub Controller for comprehensive repository and workflow management.

This module provides extensive GitHub control capabilities including:
- Repository creation, cloning, and management
- Issue and PR automation
- Advanced Git operations
- Workflow automation
- Code analysis and refactoring
- Branch management and merging
- Release management
"""

import os
import json
import time
import logging
import subprocess
from typing import Optional, Dict, List, Any, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta

try:
    import requests
    from requests.auth import HTTPBasicAuth
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import git
    from git import Repo, Git
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False


class AdvancedGitHubController:
    """Advanced GitHub automation with comprehensive repository control."""
    
    def __init__(self, token: Optional[str] = None, username: Optional[str] = None, 
                 base_url: str = "https://api.github.com"):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.username = username or os.getenv("GITHUB_USERNAME")
        self.base_url = base_url
        self.session = requests.Session() if REQUESTS_AVAILABLE else None
        
        if self.token and self.session:
            self.session.auth = HTTPBasicAuth(self.username, self.token)
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "ResearchAgent/1.0"
            })
        
        # Safety controls
        self.max_operations_per_minute = 45
        self.operation_count = 0
        self.operation_window_start = time.time()
        self.allowed_repos = set()
        self.blocked_repos = set()
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make authenticated GitHub API request with rate limiting."""
        if not self.session:
            logging.error("GitHub session not initialized")
            return None
        
        self._enforce_rate_limit()
        
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code in [200, 201, 204]:
                return response.json() if response.content else {}
            else:
                logging.error(f"GitHub API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"GitHub API request failed: {e}")
            return None
    
    def _enforce_rate_limit(self):
        """Enforce GitHub API rate limiting."""
        current_time = time.time()
        
        # Reset counter every minute
        if current_time - self.operation_window_start > 60:
            self.operation_count = 0
            self.operation_window_start = current_time
        
        # Check if we've exceeded rate limit
        if self.operation_count >= self.max_operations_per_minute:
            sleep_time = 60 - (current_time - self.operation_window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.operation_count = 0
                self.operation_window_start = time.time()
        
        self.operation_count += 1
    
    def create_repository(self, name: str, description: str = "", private: bool = False, 
                         auto_init: bool = True, gitignore_template: Optional[str] = None) -> Optional[Dict]:
        """Create a new GitHub repository."""
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init
        }
        
        if gitignore_template:
            data["gitignore_template"] = gitignore_template
        
        return self._make_request("POST", "/user/repos", data)
    
    def get_repository(self, owner: str, repo: str) -> Optional[Dict]:
        """Get repository information."""
        return self._make_request("GET", f"/repos/{owner}/{repo}")
    
    def list_repositories(self, username: Optional[str] = None, 
                         visibility: str = "all") -> List[Dict]:
        """List repositories for a user."""
        user = username or self.username
        if not user:
            return []
        
        endpoint = f"/users/{user}/repos" if user != self.username else "/user/repos"
        params = {"visibility": visibility} if visibility != "all" else {}
        
        response = self._make_request("GET", endpoint)
        return response if response else []
    
    def clone_repository(self, owner: str, repo: str, local_path: str, 
                        branch: str = "main") -> bool:
        """Clone a repository locally."""
        if not GITPYTHON_AVAILABLE:
            logging.error("GitPython not available")
            return False
        
        try:
            clone_url = f"https://github.com/{owner}/{repo}.git"
            if self.token:
                clone_url = f"https://{self.username}:{self.token}@github.com/{owner}/{repo}.git"
            
            Repo.clone_from(clone_url, local_path, branch=branch)
            return True
        except Exception as e:
            logging.error(f"Repository cloning failed: {e}")
            return False
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                    labels: List[str] = None, assignees: List[str] = None) -> Optional[Dict]:
        """Create a new issue."""
        data = {
            "title": title,
            "body": body,
            "labels": labels or [],
            "assignees": assignees or []
        }
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/issues", data)
    
    def get_issues(self, owner: str, repo: str, state: str = "open", 
                   labels: List[str] = None) -> List[Dict]:
        """Get issues for a repository."""
        params = {"state": state}
        if labels:
            params["labels"] = ",".join(labels)
        
        # Note: This is a simplified version - GitHub API uses query parameters
        endpoint = f"/repos/{owner}/{repo}/issues"
        response = self._make_request("GET", endpoint)
        return response if response else []
    
    def create_pull_request(self, owner: str, repo: str, title: str, head: str, 
                          base: str, body: str = "") -> Optional[Dict]:
        """Create a pull request."""
        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body
        }
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/pulls", data)
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get pull requests for a repository."""
        endpoint = f"/repos/{owner}/{repo}/pulls"
        response = self._make_request("GET", endpoint)
        return response if response else []
    
    def merge_pull_request(self, owner: str, repo: str, pr_number: int, 
                          merge_method: str = "merge", commit_title: str = "") -> Optional[Dict]:
        """Merge a pull request."""
        data = {
            "merge_method": merge_method,
            "commit_title": commit_title
        }
        
        return self._make_request("PUT", f"/repos/{owner}/{repo}/pulls/{pr_number}/merge", data)
    
    def create_branch(self, repo_path: str, branch_name: str, 
                     from_branch: str = "main") -> bool:
        """Create a new branch in a local repository."""
        if not GITPYTHON_AVAILABLE:
            return False
        
        try:
            repo = Repo(repo_path)
            
            # Checkout the source branch
            repo.git.checkout(from_branch)
            
            # Create and checkout new branch
            repo.git.checkout("-b", branch_name)
            
            return True
        except Exception as e:
            logging.error(f"Branch creation failed: {e}")
            return False
    
    def commit_changes(self, repo_path: str, message: str, files: List[str] = None) -> bool:
        """Commit changes to a repository."""
        if not GITPYTHON_AVAILABLE:
            return False
        
        try:
            repo = Repo(repo_path)
            
            # Add files to staging
            if files:
                for file in files:
                    repo.git.add(file)
            else:
                repo.git.add(".")
            
            # Commit changes
            repo.git.commit("-m", message)
            
            return True
        except Exception as e:
            logging.error(f"Commit failed: {e}")
            return False
    
    def push_changes(self, repo_path: str, remote: str = "origin", 
                    branch: str = "main") -> bool:
        """Push changes to remote repository."""
        if not GITPYTHON_AVAILABLE:
            return False
        
        try:
            repo = Repo(repo_path)
            repo.git.push(remote, branch)
            return True
        except Exception as e:
            logging.error(f"Push failed: {e}")
            return False
    
    def pull_changes(self, repo_path: str, remote: str = "origin", 
                    branch: str = "main") -> bool:
        """Pull changes from remote repository."""
        if not GITPYTHON_AVAILABLE:
            return False
        
        try:
            repo = Repo(repo_path)
            repo.git.pull(remote, branch)
            return True
        except Exception as e:
            logging.error(f"Pull failed: {e}")
            return False
    
    def get_file_content(self, owner: str, repo: str, path: str, 
                        branch: str = "main") -> Optional[str]:
        """Get file content from a repository."""
        response = self._make_request("GET", f"/repos/{owner}/{repo}/contents/{path}")
        if response and "content" in response:
            import base64
            return base64.b64decode(response["content"]).decode("utf-8")
        return None
    
    def create_file(self, owner: str, repo: str, path: str, content: str, 
                   message: str, branch: str = "main") -> Optional[Dict]:
        """Create a new file in a repository."""
        import base64
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch
        }
        
        return self._make_request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)
    
    def update_file(self, owner: str, repo: str, path: str, content: str, 
                    message: str, sha: str, branch: str = "main") -> Optional[Dict]:
        """Update an existing file in a repository."""
        import base64
        data = {
            "message": message,
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "sha": sha,
            "branch": branch
        }
        
        return self._make_request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)
    
    def delete_file(self, owner: str, repo: str, path: str, message: str, 
                    sha: str, branch: str = "main") -> Optional[Dict]:
        """Delete a file from a repository."""
        data = {
            "message": message,
            "sha": sha,
            "branch": branch
        }
        
        return self._make_request("DELETE", f"/repos/{owner}/{repo}/contents/{path}", data)
    
    def create_release(self, owner: str, repo: str, tag_name: str, 
                      name: str = "", body: str = "", draft: bool = False, 
                      prerelease: bool = False) -> Optional[Dict]:
        """Create a release."""
        data = {
            "tag_name": tag_name,
            "name": name or tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/releases", data)
    
    def get_releases(self, owner: str, repo: str) -> List[Dict]:
        """Get releases for a repository."""
        response = self._make_request("GET", f"/repos/{owner}/{repo}/releases")
        return response if response else []
    
    def search_repositories(self, query: str, language: Optional[str] = None, 
                          sort: str = "stars", order: str = "desc") -> List[Dict]:
        """Search for repositories."""
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        # Note: GitHub search API uses different endpoint structure
        endpoint = f"/search/repositories?q={search_query}&sort={sort}&order={order}"
        response = self._make_request("GET", endpoint)
        return response.get("items", []) if response else []
    
    def get_user_info(self, username: Optional[str] = None) -> Optional[Dict]:
        """Get user information."""
        user = username or self.username
        if not user:
            return None
        
        endpoint = "/user" if user == self.username else f"/users/{user}"
        return self._make_request("GET", endpoint)
    
    def get_organization_repositories(self, org: str) -> List[Dict]:
        """Get repositories for an organization."""
        response = self._make_request("GET", f"/orgs/{org}/repos")
        return response if response else []
    
    def fork_repository(self, owner: str, repo: str) -> Optional[Dict]:
        """Fork a repository."""
        return self._make_request("POST", f"/repos/{owner}/{repo}/forks")
    
    def star_repository(self, owner: str, repo: str) -> bool:
        """Star a repository."""
        response = self._make_request("PUT", f"/user/starred/{owner}/{repo}")
        return response is not None
    
    def unstar_repository(self, owner: str, repo: str) -> bool:
        """Unstar a repository."""
        response = self._make_request("DELETE", f"/user/starred/{owner}/{repo}")
        return response is not None
    
    def watch_repository(self, owner: str, repo: str) -> bool:
        """Watch a repository."""
        data = {"subscribed": True, "ignored": False}
        response = self._make_request("PUT", f"/repos/{owner}/{repo}/subscription", data)
        return response is not None
    
    def unwatch_repository(self, owner: str, repo: str) -> bool:
        """Unwatch a repository."""
        response = self._make_request("DELETE", f"/repos/{owner}/{repo}/subscription")
        return response is not None
    
    def get_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[str] = None) -> List[Dict]:
        """Get workflow runs for a repository."""
        endpoint = f"/repos/{owner}/{repo}/actions/runs"
        if workflow_id:
            endpoint = f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs"
        
        response = self._make_request("GET", endpoint)
        return response.get("workflow_runs", []) if response else []
    
    def trigger_workflow(self, owner: str, repo: str, workflow_id: str, 
                        ref: str = "main", inputs: Dict[str, str] = None) -> Optional[Dict]:
        """Trigger a workflow dispatch."""
        data = {
            "ref": ref,
            "inputs": inputs or {}
        }
        
        return self._make_request("POST", f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches", data)
    
    def get_rate_limit(self) -> Optional[Dict]:
        """Get current rate limit status."""
        return self._make_request("GET", "/rate_limit")
    
    def set_safety_controls(self, allowed_repos: List[str] = None, 
                           blocked_repos: List[str] = None,
                           max_operations_per_minute: int = 30):
        """Configure safety controls."""
        if allowed_repos:
            self.allowed_repos = set(allowed_repos)
        if blocked_repos:
            self.blocked_repos = set(blocked_repos)
        if max_operations_per_minute:
            self.max_operations_per_minute = max_operations_per_minute
