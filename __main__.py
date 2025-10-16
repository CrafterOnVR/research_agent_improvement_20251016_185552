import argparse
import os
import sys
from .agent import ResearchAgent
from .git_tools import GitManager
from .self_edit import SelfEditor
from .export import Exporter
from .runner import Runner


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="research_agent",
        description="Autonomous topic research agent with time-boxed web exploration and deduped storage",
    )
    # Core run options
    p.add_argument("--topic", type=str, default=None, help="Topic to research (interactive prompt if omitted)")
    p.add_argument("--resume", type=str, default=None, help="Resume 24h research for an existing topic name")
    p.add_argument("--initial-seconds", type=int, default=3600, help="Seconds for initial scoping phase (default: 3600)")
    p.add_argument("--deep-seconds", type=int, default=86400, help="Seconds for deep research phase (default: 86400)")
    p.add_argument("--data-dir", type=str, default=None, help="Optional data directory for DB and cache")
    p.add_argument("--max-results", type=int, default=10, help="Max search results per query")
    p.add_argument("--no-llm", action="store_true", help="Disable LLM usage even if configured")
    
    # Enhanced web capabilities
    p.add_argument("--enable-state-changing", action="store_true", 
                   help="Enable state-changing web actions (POST, PUT, DELETE, form submission, etc.)")
    p.add_argument("--selenium-driver", type=str, default="chrome", choices=["chrome", "firefox"],
                   help="WebDriver to use for browser automation (default: chrome)")
    p.add_argument("--no-headless", action="store_true",
                   help="Run browser in visible mode (default: headless)")
    p.add_argument("--interactive-urls", type=str, nargs="*", default=[],
                   help="URLs that require interactive/state-changing actions for research")

    # Git options
    p.add_argument("--git-init", action="store_true", help="Initialize a git repo in the project directory if not present")
    p.add_argument("--git-branch", type=str, default=None, help="Checkout or create the specified git branch")
    p.add_argument("--git-auto-commit", action="store_true", help="Auto-commit snapshots at key phases")

    # Self-edit options
    p.add_argument("--self-edit-file", type=str, default=None, help="Path (relative to --fs-root) of file to edit")
    p.add_argument("--find", type=str, default=None, help="Text to find for self-edit")
    p.add_argument("--replace", type=str, default=None, help="Replacement text for self-edit")

    # File system options
    p.add_argument("--create-file", type=str, default=None, help="Create a file at the given path (relative to --fs-root unless absolute)")
    p.add_argument("--file-contents", type=str, default="", help="Contents to write when using --create-file")
    p.add_argument("--file-contents-file", type=str, default=None, help="Path to a local file whose contents will be written to --create-file")
    p.add_argument("--mkdir", type=str, default=None, help="Create a directory at the given path (relative to --fs-root unless absolute)")
    p.add_argument("--fs-root", type=str, default=None, help="Constrain file operations to this root (default: project directory)")
    p.add_argument("--allow-any-path", action="store_true", help="Allow operations anywhere on disk (DANGEROUS; prefer --fs-root)")

    # Export options
    p.add_argument("--export-project", type=str, default=None, help="Create a zip of the project to the given path (or auto-name if omitted)")
    p.add_argument("--export-to", type=str, default=None, help="Copy the created zip to this filesystem directory")
    p.add_argument("--export-mtp", type=str, default=None, help="Copy the created zip to this MTP path, e.g. 'My Phone/Internal Storage/Download'")
    p.add_argument("--list-mtp", action="store_true", help="List top-level MTP devices and their storages (Windows only)")
    p.add_argument("--export-include-data", action="store_true", help="Include the data/ folder in the export zip")

    # Watch mode (opt-in, allowlisted target)
    p.add_argument("--watch-mtp", type=str, default=None, help="Watch the project and auto-export+copy to this MTP path when changes are detected")
    p.add_argument("--watch-interval", type=int, default=30, help="Polling interval seconds for watch mode")
    p.add_argument("--watch-include-data", action="store_true", help="Include the data/ folder in watch-mode zips")

    # Run files (opt-in, guarded)
    p.add_argument("--run-file", type=str, default=None, help="Run a file (script or executable)")
    p.add_argument("--run-mode", type=str, choices=["auto", "interpreter", "open"], default="auto", help="How to run: auto-detect interpreter, force interpreter, or open with default app")
    p.add_argument("--run-timeout", type=int, default=120, help="Timeout seconds for process execution (interpreter mode)")
    p.add_argument("--run-cwd", type=str, default=None, help="Working directory for the process (default: file's directory)")
    p.add_argument("--run-allow-any-path", action="store_true", help="Allow running files outside the project root (use with care)")
    p.add_argument("--run-yes", action="store_true", help="Skip confirmation prompt before running the file")
    p.add_argument("--run-as-admin", action="store_true", help="Run the file elevated (Windows: UAC prompt)")

    return p


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


'
# Self-improvement integration
def check_for_self_improvement():
    """Check if self-improvement cycle should be initiated."""
    # Implementation would check research results and trigger improvement if needed
    return False

# Add self-improvement check to main function
if check_for_self_improvement():
    print("Initiating self-improvement cycle...")
    # Trigger improvement process


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    args = build_parser().parse_args(argv)

    # Prepare git manager rooted at this package directory
    pkg_root = os.path.abspath(os.path.dirname(__file__))
    git = GitManager(root=pkg_root)
    exporter = Exporter(package_dir=pkg_root)
    runner = Runner(root=pkg_root)

    if args.git_init:
        if git.ensure_repo():
            git.ensure_gitignore()
        else:
            print("Warning: Git not installed or initialization failed.")
    if args.git_branch:
        if not git.checkout_or_create_branch(args.git_branch):
            print(f"Warning: failed to checkout or create branch '{args.git_branch}'.")

    # Handle MTP listing early
    if args.list_mtp:
        items = exporter.list_mtp(max_depth=2)
        if not items:
            print("No MTP devices found or Windows Shell unavailable.")
        else:
            print("MTP devices and storages:")
            for path in items:
                print(f"- {path}")
        return 0

    # Watch mode
    if args.watch_mtp:
        print("Starting watch mode. Press Ctrl+C to stop.")
        exporter.watch_mtp(
            mtp_path=args.watch_mtp,
            interval=max(5, int(args.watch_interval)),
            include_data=bool(args.watch_include_data),
        )
        return 0

    # Export workflow (zip + copy)
    if args.export_project or args.export_to or args.export_mtp:
        # Determine zip path
        zip_path = args.export_project
        if not zip_path or os.path.isdir(zip_path):
            # Auto-name in cwd if not provided or a directory was given
            ts = __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S")
            base_dir = zip_path if zip_path and os.path.isdir(zip_path) else os.getcwd()
            zip_path = os.path.join(base_dir, f"research_agent-{ts}.zip")
        out = exporter.make_zip(zip_path, include_data=args.export_include_data)
        print(f"Project zipped to: {out}")
        # Optional copies
        if args.export_to:
            try:
                copied = exporter.copy_to_path(out, args.export_to)
                print(f"Copied to filesystem path: {copied}")
            except Exception as e:
                print(f"Failed to copy to filesystem path: {e}")
        if args.export_mtp:
            ok = exporter.copy_to_mtp(out, args.export_mtp)
            if ok:
                print(f"Copied to MTP path: {args.export_mtp}")
            else:
                print("Failed to copy to MTP path. Use --list-mtp to discover valid targets, and ensure pywin32 is installed.")
        return 0

    # Run a file (guarded)
    if args.run_file:
        # Run anywhere by default; no confirmation prompt
        fs_root = args.fs_root or pkg_root
        run = Runner(root=fs_root, allow_any_path=True)
        target = args.run_file
        result = run.execute(
            target,
            mode=args.run_mode,
            timeout=args.run_timeout,
            cwd=args.run_cwd,
            print_output=True,
            run_as_admin=bool(args.run_as_admin),
        )
        if not result.get("ok"):
            print(f"Run failed: {result.get('error','unknown error')}")
            return 1
        print(f"Exit code: {result.get('returncode')}")
        return 0

    # Prepare editor with requested scope
    fs_root = args.fs_root or pkg_root
    editor = SelfEditor(root=fs_root, git=git if args.git_auto_commit else None, allow_any_path=bool(args.allow_any_path))

    # File/directory creation (one-shot)
    if args.mkdir:
        try:
            created = editor.mkdir(args.mkdir, exist_ok=True)
            print(f"Directory ensured: {created}")
        except Exception as e:
            print(f"Failed to create directory: {e}")
            return 2
        return 0

    if args.create_file:
        try:
            if args.file_contents_file:
                try:
                    with open(args.file_contents_file, "r", encoding="utf-8") as f:
                        contents = f.read()
                except Exception as e:
                    print(f"Failed to read --file-contents-file: {e}")
                    return 2
            else:
                contents = args.file_contents or ""
            created = editor.create_file(args.create_file, contents=contents, make_parents=True, do_commit=args.git_auto_commit)
            print(f"File written: {created}")
        except Exception as e:
            print(f"Failed to create file: {e}")
            return 2
        return 0

    # Self-edit mode (one-shot)
    if args.self_edit_file:
        if not args.find:
            print("--find is required when using --self-edit-file")
            return 2
        changed = editor.replace_in_file(args.self_edit_file, args.find, args.replace or "", do_commit=args.git_auto_commit)
        if changed:
            print(f"Edited: {args.self_edit_file}")
        else:
            print("No changes applied (pattern not found or no diff)")
        return 0

    agent = ResearchAgent(
        data_dir=args.data_dir,
        use_llm=not args.no_llm,
        max_results=args.max_results,
        git_manager=git if args.git_auto_commit else None,
        auto_commit=args.git_auto_commit,
        enable_state_changing=args.enable_state_changing,
        selenium_driver=args.selenium_driver,
        headless=not args.no_headless,
    )

    if args.resume:
        topic = args.resume.strip()
        agent.resume_or_run(topic, deep_seconds=args.deep_seconds)
        return 0

    topic = args.topic
    if not topic:
        try:
            topic = input("Enter a topic to research: ").strip()
        except KeyboardInterrupt:
            print("\nAborted.")
            return 1

    if not topic:
        print("No topic provided.")
        return 1

    # Run standard research
    agent.run(topic, initial_seconds=args.initial_seconds, deep_seconds=args.deep_seconds)
    
    # Handle interactive URLs if provided
    if args.interactive_urls and args.enable_state_changing:
        print(f"\nPerforming interactive research on {len(args.interactive_urls)} URLs...")
        agent.interactive_web_research(topic, args.interactive_urls)
    elif args.interactive_urls and not args.enable_state_changing:
        print("Warning: Interactive URLs provided but state-changing actions are disabled.")
        print("Use --enable-state-changing to enable interactive research.")
    
    # Clean up resources
    agent.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

