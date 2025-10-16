import os
import time
from datetime import datetime, timezone
from typing import Optional, List

try:
    # Try relative imports first (for package execution)
    from .db import Database
    from .search import Searcher
    from .fetch import Fetcher
    from .llm import LLMClient
    from .git_tools import GitManager
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from db import Database
    from search import Searcher
    from fetch import Fetcher
    from llm import LLMClient
    from git_tools import GitManager


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ResearchAgent:
    def __init__(self, data_dir: Optional[str] = None, use_llm: bool = True, max_results: int = 10,
                 git_manager: Optional[GitManager] = None, auto_commit: bool = False,
                 enable_state_changing: bool = False, selenium_driver: str = "chrome",
                 headless: bool = True):
        # Default data directory inside the package to keep repo self-contained
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "research.db")
        self.db = Database(self.db_path)
        self.searcher = Searcher(max_results=max_results)
        self.fetcher = Fetcher(enable_state_changing=enable_state_changing,
                             selenium_driver=selenium_driver, headless=headless)
        self.llm = LLMClient(enabled=use_llm)
        self.git = git_manager
        self.auto_commit = auto_commit
        self.enable_state_changing = enable_state_changing

    def run(self, topic_name: str, initial_seconds: int = 3600, deep_seconds: int = 86400):
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Topic: '{topic_name}' (id={topic_id})")

        print(f"\nPhase 1: Initial research (~{initial_seconds} seconds)")
        self._commit_snapshot("chore: snapshot before initial research")
        self.initial_research(topic_id, topic_name, seconds=initial_seconds)
        self._commit_snapshot(f"feat: initial research complete for '{topic_name}'")

        print(f"\nPhase 2: Question-driven deep research (~{deep_seconds} seconds)")
        self.deep_research(topic_id, topic_name, seconds=deep_seconds)
        self._commit_snapshot(f"feat: deep research cycle complete for '{topic_name}'")

        self._post_cycle_prompt(topic_id, topic_name, deep_seconds)

    def resume_or_run(self, topic_name: str, deep_seconds: int = 86400):
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Resuming deep research for topic: '{topic_name}' (id={topic_id})")
        self._commit_snapshot("chore: snapshot before deep research resume")
        self.deep_research(topic_id, topic_name, seconds=deep_seconds)
        self._commit_snapshot(f"feat: deep research resume cycle complete for '{topic_name}'")
        self._post_cycle_prompt(topic_id, topic_name, deep_seconds)

    # ----- Phases -----
    def initial_research(self, topic_id: int, topic_name: str, seconds: int):
        deadline = time.monotonic() + max(0, seconds)
        base_queries = [
            f"what is {topic_name}",
            f"all about {topic_name}",
            f"introduction to {topic_name}",
            f"beginner guide {topic_name}",
        ]
        seen_urls = set()
        for q in base_queries:
            if time.monotonic() >= deadline:
                break
            for r in self.searcher.search(q):
                if time.monotonic() >= deadline:
                    break
                url = r.get("href") or r.get("url")
                title = r.get("title")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                text = self.fetcher.fetch_text(url)
                if not text:
                    continue
                added, doc_id = self.db.add_document(topic_id, url, title or "", text, created_at=utc_now_iso())
                if added:
                    self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                    print(f"Saved: {title or url}")
                time.sleep(1.0)  # be polite

        # Seed question list for deep phase
        self._ensure_questions(topic_id, topic_name)

    def deep_research(self, topic_id: int, topic_name: str, seconds: int):
        deadline = time.monotonic() + max(0, seconds)
        self._ensure_questions(topic_id, topic_name)
        while time.monotonic() < deadline:
            q = self.db.pop_next_pending_question(topic_id)
            if not q:
                # regenerate if empty
                self._ensure_questions(topic_id, topic_name, regen=True)
                q = self.db.pop_next_pending_question(topic_id)
                if not q:
                    break
            qid, question = q
            # Drive search by question
            for r in self.searcher.search(f"{question} {topic_name}"):
                if time.monotonic() >= deadline:
                    break
                url = r.get("href") or r.get("url")
                title = r.get("title")
                if not url:
                    continue
                text = self.fetcher.fetch_text(url)
                if not text:
                    continue
                added, doc_id = self.db.add_document(topic_id, url, title or "", text, created_at=utc_now_iso())
                if added:
                    self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                    print(f"[Q] {question}\n    -> Saved: {title or url}")
                time.sleep(1.0)
            self.db.mark_question_done(qid)

    # ----- Helpers -----
    def _ensure_questions(self, topic_id: int, topic_name: str, regen: bool = False, target: int = 40):
        pending_count = self.db.count_pending_questions(topic_id)
        if not regen and pending_count >= 10:
            return
        # Build lightweight context from a few docs
        docs = self.db.get_recent_docs(topic_id, limit=8)
        context = "\n\n".join([
            f"Title: {d['title']}\nExcerpt: {self.db.make_excerpt(d['content'])}"
            for d in docs
        ])
        questions: List[str]
        if self.llm.enabled:
            questions = self.llm.generate_questions(topic_name, context, target=target)
        else:
            questions = self._heuristic_questions(topic_name, context, target)
        now = utc_now_iso()
        self.db.add_questions(topic_id, questions, asked_at=now)

    def _heuristic_questions(self, topic: str, context: str, target: int) -> List[str]:
        seeds = [
            f"What are the core concepts of {topic}?",
            f"How is {topic} used in practice?",
            f"What are common misconceptions about {topic}?",
            f"What tools and libraries support {topic}?",
            f"What are the historical milestones of {topic}?",
            f"What are the pros and cons of {topic}?",
            f"How does {topic} compare to alternatives?",
            f"What are the best resources to learn {topic}?",
            f"What are advanced topics within {topic}?",
            f"What are current trends related to {topic}?",
        ]
        # Simple expansion
        extras = [f"Explain {topic} for beginners.", f"Explain {topic} for experts.", f"Case studies about {topic}."]
        out = seeds + extras
        return out[:target]

    def _post_cycle_prompt(self, topic_id: int, topic_name: str, deep_seconds: int):
        print("\nResearch cycle complete.")
        while True:
            try:
                choice = input("Continue researching another 24h (c) or summarize (s)? [c/s]: ").strip().lower()
            except KeyboardInterrupt:
                print("\nAborted.")
                return
            if choice in {"c", "s"}:
                break
        if choice == "c":
            self.deep_research(topic_id, topic_name, seconds=deep_seconds)
            return self._post_cycle_prompt(topic_id, topic_name, deep_seconds)
        else:
            self._commit_snapshot("chore: snapshot before summarization")
            self.summarize_topic(topic_id, topic_name)
            self._commit_snapshot(f"docs: summary generated for '{topic_name}'")

    def summarize_topic(self, topic_id: int, topic_name: str):
        docs = self.db.get_recent_docs(topic_id, limit=20)
        context = "\n\n".join([
            f"Title: {d['title']}\nExcerpt: {self.db.make_excerpt(d['content'])}"
            for d in docs
        ])
        if self.llm.enabled:
            summary = self.llm.summarize(topic_name, context)
        else:
            summary = self._heuristic_summary(topic_name, context)
        print("\n===== Summary =====\n")
        print(summary)
        print("\n===================\n")

    # Enhanced web interaction methods
    def fetch_with_selenium(self, url: str, wait_for_element: Optional[str] = None, 
                           wait_timeout: int = 10) -> Optional[str]:
        """Fetch content using Selenium for JavaScript-heavy sites"""
        if not self.enable_state_changing:
            print("Warning: State-changing actions are disabled. Using regular fetch.")
            return self.fetcher.fetch_text(url)
        
        print(f"Fetching with Selenium: {url}")
        return self.fetcher.fetch_with_selenium(url, wait_for_element, wait_timeout)

    def submit_form(self, url: str, form_data: dict, form_selector: Optional[str] = None) -> Optional[dict]:
        """Submit a form and return the result"""
        if not self.enable_state_changing:
            raise ValueError("State-changing actions are disabled. Use --enable-state-changing to enable.")
        
        print(f"Submitting form to: {url}")
        return self.fetcher.submit_form(url, form_data, form_selector)

    def make_api_request(self, url: str, method: str = "GET", data: Optional[dict] = None, 
                        headers: Optional[dict] = None) -> Optional[dict]:
        """Make API requests with various HTTP methods"""
        if not self.enable_state_changing and method != "GET":
            raise ValueError("State-changing actions are disabled. Use --enable-state-changing to enable.")
        
        print(f"Making {method} request to: {url}")
        return self.fetcher.make_api_request(url, method, data, headers)

    def interactive_web_research(self, topic_name: str, interactive_urls: List[str]):
        """Perform interactive research on specific URLs that require state-changing actions"""
        if not self.enable_state_changing:
            print("Warning: Interactive web research requires state-changing actions to be enabled.")
            return
        
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Starting interactive research for '{topic_name}' on {len(interactive_urls)} URLs")
        
        for url in interactive_urls:
            try:
                # Try to fetch with Selenium first
                text = self.fetcher.fetch_with_selenium(url)
                if text:
                    added, doc_id = self.db.add_document(topic_id, url, f"Interactive: {url}", text, created_at=utc_now_iso())
                    if added:
                        self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                        print(f"    -> Saved interactive content: {url}")
                else:
                    print(f"    -> Failed to fetch: {url}")
            except Exception as e:
                print(f"    -> Error with {url}: {e}")
            
            time.sleep(2)  # Be respectful

    def close(self):
        """Clean up resources"""
        if hasattr(self.fetcher, 'close'):
            self.fetcher.close()

    def _heuristic_summary(self, topic: str, context: str) -> str:
        lines = [l.strip() for l in context.splitlines() if l.strip()]
        head = lines[:20]
        bullet = "\n- ".join([l[:160] for l in head])
        return f"Topic: {topic}\n- {bullet}"

    # ----- Git helpers -----
    def _commit_snapshot(self, message: str):
        if self.auto_commit and self.git is not None:
            try:
                self.git.commit_all(message)
            except Exception:
                pass

