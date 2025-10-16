import os
import subprocess
from typing import Optional


class GitManager:
    def __init__(self, root: Optional[str] = None):
        # Default root is the package directory (where this code lives)
        self.root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), ""))

    # ---------- detection ----------
    def is_git_installed(self) -> bool:
        try:
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

    def is_repo(self) -> bool:
        if not self.is_git_installed():
            return False
        try:
            r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=self.root, capture_output=True, text=True, check=True)
            return r.stdout.strip().lower() == "true"
        except Exception:
            # Fallback: detect .git directory
            return os.path.isdir(os.path.join(self.root, ".git"))

    # ---------- setup ----------
    def ensure_repo(self, default_branch: str = "main") -> bool:
        """Ensure a repo exists in root. Returns True if a repo exists (created or pre-existing)."""
        if not self.is_git_installed():
            return False
        if self.is_repo():
            return True
        # Try git init -b, fallback to plain init + checkout -b
        try:
            try:
                subprocess.run(["git", "init", "-b", default_branch], cwd=self.root, check=True)
            except Exception:
                subprocess.run(["git", "init"], cwd=self.root, check=True)
                # Create branch if possible
                subprocess.run(["git", "checkout", "-b", default_branch], cwd=self.root, check=False)
            return True
        except Exception:
            return False

    def ensure_gitignore(self, lines: Optional[str] = None):
        path = os.path.join(self.root, ".gitignore")
        if os.path.exists(path):
            return
        content = lines or DEFAULT_GITIGNORE
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    # ---------- branch ----------
    def checkout_or_create_branch(self, name: str) -> bool:
        if not self.is_git_installed() or not self.is_repo():
            return False
        try:
            # Try checkout existing
            r = subprocess.run(["git", "rev-parse", "--verify", name], cwd=self.root, capture_output=True, text=True)
            if r.returncode == 0:
                subprocess.run(["git", "checkout", name], cwd=self.root, check=True)
                return True
            # Create new
            subprocess.run(["git", "checkout", "-b", name], cwd=self.root, check=True)
            return True
        except Exception:
            return False

    # ---------- commit ----------
    def status_porcelain(self) -> str:
        if not self.is_git_installed() or not self.is_repo():
            return ""
        try:
            r = subprocess.run(["git", "status", "--porcelain"], cwd=self.root, capture_output=True, text=True, check=True)
            return r.stdout
        except Exception:
            return ""

    def commit_all(self, message: str) -> bool:
        if not self.is_git_installed() or not self.is_repo():
            return False
        try:
            subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
            status = self.status_porcelain()
            if not status.strip():
                return False
            subprocess.run(["git", "commit", "-m", message], cwd=self.root, check=True)
            return True
        except Exception:
            return False


DEFAULT_GITIGNORE = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
.venv/
venv/
ENV/
.env

# IDEs and editors
.vscode/
.idea/
*.swp

# Logs
*.log

# macOS
.DS_Store

# Windows
Thumbs.db

# Project data
# If data is kept inside this package (default)
data/
# If using the older default (sibling dir), keep this here for reference
# ../research_agent_data/
"""

