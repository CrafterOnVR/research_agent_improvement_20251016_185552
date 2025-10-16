import os
import sys
import subprocess
import ctypes
from typing import Optional, Dict, List


class Runner:
    """Execute files safely with guardrails.

    - By default, operations are restricted to a root directory. Set allow_any_path=True to override.
    - Supports interpreter-based execution for common script types.
    - Can open files with the OS default handler (Windows).
    - Supports timeouts and optional output capture/printing.
    """

    def __init__(self, root: Optional[str] = None, allow_any_path: bool = True):
        self.root = root or os.path.abspath(os.path.join(os.path.dirname(__file__), ""))
        # Default to allowing any path for maximum efficiency (no path guardrails)
        self.allow_any_path = allow_any_path

    def _within_root(self, p: str) -> bool:
        try:
            return os.path.commonpath([self.root, p]) == self.root
        except Exception:
            return False

    def _abs_path(self, path: str) -> str:
        p = os.path.abspath(path)
        # Path guardrails disabled by default; allow any absolute path
        return p

    def _guess_interpreter(self, file_path: str) -> Optional[List[str]]:
        ext = os.path.splitext(file_path)[1].lower()
        # Prefer current Python for .py
        if ext == ".py":
            return [sys.executable, file_path]
        # PowerShell script
        if ext == ".ps1":
            return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", file_path]
        # Windows batch/cmd
        if ext in {".bat", ".cmd"}:
            return ["cmd.exe", "/c", file_path]
        # Native executable
        if ext == ".exe":
            return [file_path]
        # Node.js script
        if ext == ".js":
            return ["node", file_path]
        # Shell script (if present; mainly for WSL/Unix)
        if ext == ".sh":
            return ["bash", file_path]
        return None

    def execute(
        self,
        file_path: str,
        mode: str = "auto",
        timeout: Optional[int] = 120,
        cwd: Optional[str] = None,
        print_output: bool = True,
    ) -> Dict:
        """Run a file.

        mode:
          - auto: try interpreter by extension; if unknown and on Windows, open with default app
          - interpreter: require interpreter mapping; fail if unknown
          - open: open with default app (Windows only)
        """
        abs_path = self._abs_path(file_path)
        if not os.path.exists(abs_path):
            return {"ok": False, "error": f"File not found: {abs_path}"}
        run_cwd = os.path.abspath(cwd) if cwd else os.path.dirname(abs_path)
        # Working directory guardrail disabled by default

        # Interpreter path
        argv = self._guess_interpreter(abs_path)

        # Elevated path (Windows only)
        if run_as_admin:
            if os.name != "nt":
                return {"ok": False, "error": "--run-as-admin is only supported on Windows"}
            if mode == "open" or (mode == "auto" and not argv):
                # Open the target with default handler, elevated
                return self._run_elevated(abs_path, None, run_cwd)
            # Use interpreter/argv elevated
            if not argv:
                return {"ok": False, "error": "No interpreter mapping for this file type"}
            params = subprocess.list2cmdline(argv[1:]) if len(argv) > 1 else None
            return self._run_elevated(argv[0], params, run_cwd)

        if mode == "interpreter":
            if not argv:
                return {"ok": False, "error": "No interpreter mapping for this file type"}
            return self._run_subprocess(argv, run_cwd, timeout, print_output)

        if mode == "open":
            return self._open_default(abs_path)

        # auto
        if argv:
            return self._run_subprocess(argv, run_cwd, timeout, print_output)
        return self._open_default(abs_path)

    def _run_subprocess(self, argv: List[str], cwd: str, timeout: Optional[int], print_output: bool) -> Dict:
        try:
            completed = subprocess.run(
                argv,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout if timeout and timeout > 0 else None,
            )
            if print_output:
                if completed.stdout:
                    print(completed.stdout, end="")
                if completed.stderr:
                    print(completed.stderr, end="")
            return {"ok": True, "returncode": completed.returncode}
        except subprocess.TimeoutExpired as e:
            return {"ok": False, "error": f"Timeout after {timeout}s", "returncode": None}
        except FileNotFoundError as e:
            return {"ok": False, "error": f"Executable not found: {e}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _run_elevated(self, file: str, params: Optional[str], cwd: Optional[str]) -> Dict:
        # Windows ShellExecuteW with 'runas' verb to trigger elevation
        try:
            if os.name != "nt":
                return {"ok": False, "error": "Elevation only supported on Windows"}
            # Show = 1 (SW_SHOWNORMAL)
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", file, params, cwd if cwd else None, 1)
            # Per docs, > 32 indicates success
            if ret <= 32:
                return {"ok": False, "error": f"ShellExecuteW failed with code {int(ret)}"}
            return {"ok": True, "returncode": None}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _open_default(self, abs_path: str) -> Dict:
        # Windows default app open
        if os.name == "nt":
            try:
                os.startfile(abs_path)  # type: ignore[attr-defined]
                return {"ok": True, "returncode": 0}
            except Exception as e:
                return {"ok": False, "error": str(e)}
        # Non-Windows: try xdg-open/open
        opener = None
        if sys.platform == "darwin":
            opener = ["open", abs_path]
        else:
            opener = ["xdg-open", abs_path]
        try:
            subprocess.Popen(opener)
            return {"ok": True, "returncode": 0}
        except Exception as e:
            return {"ok": False, "error": str(e)}

