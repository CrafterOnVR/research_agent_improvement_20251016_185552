import os
import zipfile
import shutil
import hashlib
import time
from typing import List, Optional

try:
    import win32com.client  # type: ignore
    HAVE_WIN32 = True
except Exception:  # pragma: no cover
    HAVE_WIN32 = False


EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "env", "venv", "ENV", ".idea", ".vscode"}
EXCLUDE_FILES = {"Thumbs.db", ".DS_Store"}


class Exporter:
    def __init__(self, package_dir: Optional[str] = None):
        # Directory containing the research_agent package
        self.pkg_dir = package_dir or os.path.abspath(os.path.dirname(__file__))
        self.parent_dir = os.path.dirname(self.pkg_dir)

    def make_zip(self, zip_path: str, include_data: bool = False) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(zip_path)), exist_ok=True)
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.pkg_dir):
                # Prune excluded dirs
                pruned = []
                for d in list(dirs):
                    if d in EXCLUDE_DIRS or (not include_data and d == "data"):
                        pruned.append(d)
                for d in pruned:
                    dirs.remove(d)
                # Add files
                for fn in files:
                    if fn in EXCLUDE_FILES:
                        continue
                    full = os.path.join(root, fn)
                    rel_from_parent = os.path.relpath(full, self.parent_dir)
                    # Ensure the zip contains the research_agent/ prefix
                    zf.write(full, rel_from_parent)
        return os.path.abspath(zip_path)

    def copy_to_path(self, src_file: str, dest_dir: str) -> str:
        dest_dir_abs = os.path.abspath(dest_dir)
        os.makedirs(dest_dir_abs, exist_ok=True)
        dest_file = os.path.join(dest_dir_abs, os.path.basename(src_file))
        shutil.copy2(src_file, dest_file)
        return dest_file

    def list_mtp(self, max_depth: int = 2) -> List[str]:
        if not HAVE_WIN32:
            return []
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.NameSpace("shell:MyComputerFolder")
            if folder is None:
                return []
            out: List[str] = []
            def walk(shell_folder, path_parts: List[str], depth: int):
                if depth > max_depth:
                    return
                items = shell_folder.Items()
                for i in items:
                    name = str(i.Name)
                    new_parts = path_parts + [name]
                    out.append("/".join(new_parts))
                    if depth < max_depth:
                        try:
                            subf = i.GetFolder()
                        except Exception:
                            subf = None
                        if subf is not None:
                            walk(subf, new_parts, depth + 1)
            walk(folder, [], 0)
            return out
        except Exception:
            return []

    def copy_to_mtp(self, src_file: str, mtp_path: str) -> bool:
        if not HAVE_WIN32:
            return False
        parts = [p for p in mtp_path.replace("\\", "/").split("/") if p]
        if not parts:
            return False
        try:
            shell = win32com.client.Dispatch("Shell.Application")
            folder = shell.NameSpace("shell:MyComputerFolder")
            if folder is None:
                return False
            for part in parts:
                target = None
                for item in folder.Items():
                    if str(item.Name).strip().lower() == part.strip().lower():
                        target = item
                        break
                if target is None:
                    return False
                try:
                    folder = target.GetFolder()
                except Exception:
                    return False
                if folder is None:
                    return False
            # Copy file into the final folder
            folder.CopyHere(os.path.abspath(src_file))
            return True
        except Exception:
            return False

    # ---------- Watch mode ----------
    def _project_digest(self, include_data: bool = False) -> str:
        h = hashlib.sha256()
        for root, dirs, files in os.walk(self.pkg_dir):
            # Prune excluded dirs
            for d in list(dirs):
                if d in EXCLUDE_DIRS or (not include_data and d == "data"):
                    dirs.remove(d)
            for fn in sorted(files):
                if fn in EXCLUDE_FILES:
                    continue
                full = os.path.join(root, fn)
                try:
                    st = os.stat(full)
                except Exception:
                    continue
                rel = os.path.relpath(full, self.parent_dir)
                h.update(rel.encode("utf-8", errors="ignore"))
                h.update(str(int(st.st_mtime)).encode())
                h.update(str(st.st_size).encode())
        return h.hexdigest()

    def watch_mtp(self, mtp_path: str, interval: int = 30, include_data: bool = False, log_file: Optional[str] = None):
        """Poll the project for changes and auto-export+copy to the allowlisted MTP path.

        - Only targets the specific mtp_path provided by the user
        - Never touches other devices or paths
        - Creates/overwrites a single zip adjacent to the project: research_agent-watch.zip
        - Copies only when a change digest is detected since the last successful copy
        """
        out_zip = os.path.join(self.parent_dir, "research_agent-watch.zip")
        last_digest: Optional[str] = None
        log_path = log_file or os.path.join(self.pkg_dir, "logs", "export_watch.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        def log(msg: str):
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"[{ts}] {msg}\n")
            except Exception:
                pass
            print(msg)
        log(f"Watch started: interval={interval}s, include_data={include_data}, target='{mtp_path}'")
        try:
            while True:
                try:
                    digest = self._project_digest(include_data=include_data)
                    if last_digest is None or digest != last_digest:
                        # Create zip
                        self.make_zip(out_zip, include_data=include_data)
                        log(f"Zip created: {out_zip}")
                        # Attempt MTP copy
                        ok = self.copy_to_mtp(out_zip, mtp_path)
                        if ok:
                            last_digest = digest
                            log(f"Copied to MTP: {mtp_path}")
                        else:
                            log("MTP copy failed (device locked, path missing, or pywin32 unavailable)")
                    else:
                        # No change detected
                        pass
                except Exception as e:
                    log(f"Watch iteration error: {e}")
                time.sleep(max(5, int(interval)))
        except KeyboardInterrupt:
            log("Watch stopped by user")
            return

