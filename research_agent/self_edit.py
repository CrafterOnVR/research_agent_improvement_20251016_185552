import os
from typing import Optional
import datetime

try:
    # Try relative imports first (for package execution)
    from .git_tools import GitManager
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from git_tools import GitManager


class SelfEditor:
    """Safe self-editor and file manager.

    - By default, blocks operations on critical system files and directories.
    - Supports find/replace edits, file creation, and directory creation.
    - Can optionally allow operations anywhere on disk when allow_any_path=True.
    - Optionally commits changes via GitManager when the target path is inside the project root.
    """

    # Critical system paths that are blocked by default
    CRITICAL_PATHS = [
        os.path.normcase(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'))),
        os.path.normcase('C:\\Program Files'),
        os.path.normcase('C:\\Program Files (x86)'),
        os.path.normcase('C:\\ProgramData'),
        os.path.normcase('C:\\System Volume Information'),
        os.path.normcase('C:\\$Recycle.Bin'),
        os.path.normcase('C:\\Recovery'),
        os.path.normcase('C:\\Boot'),
    ]

    def __init__(self, root: Optional[str] = None, git: Optional[GitManager] = None, allow_any_path: bool = False):
        self.root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
        self.git = git
        self.allow_any_path = allow_any_path

    def _is_critical_path(self, p: str) -> bool:
        """Check if the path is within a critical system directory."""
        try:
            norm_p = os.path.normcase(os.path.abspath(p))
            return any(norm_p.startswith(critical) for critical in self.CRITICAL_PATHS)
        except Exception:
            return False

    def _within_root(self, p: str) -> bool:
        """Check if the path is within the project root (for git operations)."""
        try:
            return os.path.commonpath([self.root, p]) == self.root
        except Exception:
            return False

    def _abs_path(self, path: str) -> str:
        # Resolve absolute path
        p = os.path.abspath(os.path.join(self.root, path)) if not os.path.isabs(path) else os.path.abspath(path)
        # Enforce that the path is not critical unless explicitly allowed
        if not self.allow_any_path and self._is_critical_path(p):
            raise ValueError("Path targets critical system files. Pass allow_any_path=True to override.")
        return p

    def _log_activity(self, action: str, path: str, message: Optional[str] = None):
        timestamp = datetime.datetime.now().isoformat()
        log_path = os.path.join(self.root, 'goal_log.txt')
        log_entry = f"[{timestamp}] {action}: {os.path.relpath(path, self.root)}\n"
        if message:
            log_entry += f"  Goal: {message}\n"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def replace_in_file(self, file_path: str, find: str, replace: str, do_commit: bool = False, message: Optional[str] = None) -> bool:
        abs_path = self._abs_path(file_path)
        try:
            if not os.path.exists(abs_path):
                raise FileNotFoundError(abs_path)
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()
            if find not in content:
                return False
            new_content = content.replace(find, replace)
            if new_content == content:
                return False
            # Write back
            with open(abs_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_content)
        except (IOError, OSError) as e:
            raise IOError(f"Error during file operation in replace_in_file: {e}") from e

        # Log the activity
        log_message = message or f"chore(self-edit): replace text in {os.path.relpath(abs_path, self.root)}"
        self._log_activity("replace_in_file", abs_path, log_message)

        # Optional commit if inside root
        if do_commit and self.git is not None and self._within_root(abs_path):
            self.git.commit_all(log_message)
        return True

    def create_file(self, file_path: str, contents: str = "", make_parents: bool = True, do_commit: bool = False, message: Optional[str] = None) -> str:
        abs_path = self._abs_path(file_path)
        parent = os.path.dirname(abs_path)
        if make_parents and parent:
            os.makedirs(parent, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(contents)

        # Log the activity
        log_message = message or f"feat(self-edit): create file {os.path.relpath(abs_path, self.root)}"
        self._log_activity("create_file", abs_path, log_message)

        if do_commit and self.git is not None and self._within_root(abs_path):
            self.git.commit_all(log_message)
        return abs_path

    def mkdir(self, dir_path: str, exist_ok: bool = True) -> str:
        abs_path = self._abs_path(dir_path)
        os.makedirs(abs_path, exist_ok=exist_ok)
        return abs_path

    def append_to_file(self, file_path: str, content: str, do_commit: bool = False, message: Optional[str] = None) -> bool:
        abs_path = self._abs_path(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(abs_path)
        
        with open(abs_path, "a", encoding="utf-8") as f:
            f.write(content)
        
        log_message = message or f"chore(self-edit): append to {os.path.relpath(abs_path, self.root)}"
        self._log_activity("append_to_file", abs_path, log_message)
        
        if do_commit and self.git is not None and self._within_root(abs_path):
            self.git.commit_all(log_message)
            
        return True

    def delete_file(self, file_path: str, do_commit: bool = False, message: Optional[str] = None) -> bool:
        abs_path = self._abs_path(file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(abs_path)
        
        os.remove(abs_path)
        
        log_message = message or f"chore(self-edit): delete {os.path.relpath(abs_path, self.root)}"
        self._log_activity("delete_file", abs_path, log_message)
        
        if do_commit and self.git is not None and self._within_root(abs_path):
            self.git.commit_all(log_message)
            
        return True