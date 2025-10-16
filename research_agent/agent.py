import os
import time
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Any

try:
    # Try relative imports first (for package execution)
    from .db import Database
    from .search import Searcher
    from .fetch import Fetcher
    from .llm import LLMClient
    from .git_tools import GitManager
    from .dynamic_tool_generator import DynamicToolGenerator
except ImportError:
    # Fallback to absolute imports (for direct execution)
    from db import Database
    from search import Searcher
    from fetch import Fetcher
    from llm import LLMClient
    from git_tools import GitManager
    from dynamic_tool_generator import DynamicToolGenerator


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
        self.tool_generator = DynamicToolGenerator(self.llm)

    async def create_tool(self, tool_name: str, tool_description: str) -> Optional[Any]:
        """Creates a new tool and adds it to the agent."""
        tool = await self.tool_generator.generate_tool(tool_name, tool_description)
        if tool:
            print(f"New tool '{tool_name}' created and imported.")
            # You can now use the tool, for example:
            # result = tool.your_function_name("some_input")
            # print(f"Tool output: {result}")
        else:
            print(f"Failed to create tool '{tool_name}'.")
        return tool



    async def run(self, topic_name: str, initial_seconds: int = 3600, deep_seconds: int = 86400):
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Topic: '{topic_name}' (id={topic_id})")

        print(f"\nPhase 1: Initial research (~{initial_seconds} seconds)")
        self._commit_snapshot("chore: snapshot before initial research")
        await self.initial_research(topic_id, topic_name, seconds=initial_seconds)
        self._commit_snapshot(f"feat: initial research complete for '{topic_name}'")

        print(f"\nPhase 2: Question-driven deep research (~{deep_seconds} seconds)")
        await self.deep_research(topic_id, topic_name, seconds=deep_seconds)
        self._commit_snapshot(f"feat: deep research cycle complete for '{topic_name}'")

        await self._post_cycle_prompt(topic_id, topic_name, deep_seconds)

    async def resume_or_run(self, topic_name: str, deep_seconds: int = 86400):
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Resuming deep research for topic: '{topic_name}' (id={topic_id})")
        self._commit_snapshot("chore: snapshot before deep research resume")
        await self.deep_research(topic_id, topic_name, seconds=deep_seconds)
        self._commit_snapshot(f"feat: deep research resume cycle complete for '{topic_name}'")
        await self._post_cycle_prompt(topic_id, topic_name, deep_seconds)

    # ----- Phases -----
    async def initial_research(self, topic_id: int, topic_name: str, seconds: int):
        deadline = time.monotonic() + max(0, seconds)
        base_queries = [
            f"what is {topic_name}",
            f"all about {topic_name}",
            f"introduction to {topic_name}",
            f"beginner guide {topic_name}",
        ]
        seen_urls = set()

        async def fetch_and_return_url(url):
            text = await self.fetcher.fetch_text(url)
            return url, text

        async def search_and_fetch(query):
            if time.monotonic() >= deadline:
                return
            search_results = self.searcher.search(query)
            tasks = []
            for r in search_results:
                if time.monotonic() >= deadline:
                    break
                url = r.get("href") or r.get("url")
                title = r.get("title")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                tasks.append(fetch_and_return_url(url))
            
            fetched_results = await asyncio.gather(*tasks)
            
            for url, text in fetched_results:
                if text:
                    added, doc_id = self.db.add_document(topic_id, url, "", text, created_at=utc_now_iso())
                    if added:
                        self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                        print(f"Saved: {url}")

        await asyncio.gather(*[search_and_fetch(q) for q in base_queries])

        # Seed question list for deep phase
        await self._ensure_questions(topic_id, topic_name)

    async def deep_research(self, topic_id: int, topic_name: str, seconds: int):
        deadline = time.monotonic() + max(0, seconds)
        await self._ensure_questions(topic_id, topic_name)

        async def fetch_and_return_url(url):
            text = await self.fetcher.fetch_text(url)
            return url, text

        while time.monotonic() < deadline:
            q = self.db.pop_next_pending_question(topic_id)
            if not q:
                # regenerate if empty
                await self._ensure_questions(topic_id, topic_name, regen=True)
                q = self.db.pop_next_pending_question(topic_id)
                if not q:
                    break
            qid, question = q
            # Drive search by question
            search_results = self.searcher.search(f"{question} {topic_name}")
            tasks = []
            for r in search_results:
                if time.monotonic() >= deadline:
                    break
                url = r.get("href") or r.get("url")
                title = r.get("title")
                if not url:
                    continue
                tasks.append(fetch_and_return_url(url))

            fetched_results = await asyncio.gather(*tasks)

            for url, text in fetched_results:
                if text:
                    added, doc_id = self.db.add_document(topic_id, url, "", text, created_at=utc_now_iso())
                    if added:
                        self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                        print(f"[Q] {question}\n    -> Saved: {url}")

            self.db.mark_question_done(qid)

    # ----- Helpers -----
    async def _ensure_questions(self, topic_id: int, topic_name: str, regen: bool = False, target: int = 40):
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
            questions = await self.llm.generate_questions(topic_name, context, target=target)
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

    async def _post_cycle_prompt(self, topic_id: int, topic_name: str, deep_seconds: int):
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
            await self.deep_research(topic_id, topic_name, seconds=deep_seconds)
            return await self._post_cycle_prompt(topic_id, topic_name, deep_seconds)
        else:
            self._commit_snapshot("chore: snapshot before summarization")
            await self.summarize_topic(topic_id, topic_name)
            self._commit_snapshot(f"docs: summary generated for '{topic_name}'")

        async def summarize_topic(self, topic_id: int, topic_name: str):

            docs = self.db.get_recent_docs(topic_id, limit=20)

            context = "\n\n".join([

                f"Title: {d['title']}\nExcerpt: {self.db.make_excerpt(d['content'])} "

                for d in docs

            ])

            if self.llm.enabled:

                summary = await self.llm.summarize(topic_name, context)

            else:

                summary = self._heuristic_summary(topic_name, context)

            print("\n===== Summary =====\n")

            print(summary)

            print("\n===================\n")

            return summary

    # Enhanced web interaction methods
    async def fetch_with_selenium(self, url: str, wait_for_element: Optional[str] = None, 
                           wait_timeout: int = 10) -> Optional[str]:
        """Fetch content using Selenium for JavaScript-heavy sites"""
        if not self.enable_state_changing:
            print("Warning: State-changing actions are disabled. Using regular fetch.")
            return await self.fetcher.fetch_text(url)
        
        print(f"Fetching with Selenium: {url}")
        return await self.fetcher.fetch_with_selenium(url, wait_for_element, wait_timeout)

    async def submit_form(self, url: str, form_data: dict, form_selector: Optional[str] = None) -> Optional[dict]:
        """Submit a form and return the result"""
        if not self.enable_state_changing:
            raise ValueError("State-changing actions are disabled. Use --enable-state-changing to enable.")
        
        print(f"Submitting form to: {url}")
        return await self.fetcher.submit_form(url, form_data, form_selector)

    async def make_api_request(self, url: str, method: str = "GET", data: Optional[dict] = None, 
                        headers: Optional[dict] = None) -> Optional[dict]:
        """Make API requests with various HTTP methods"""
        if not self.enable_state_changing and method != "GET":
            raise ValueError("State-changing actions are disabled. Use --enable-state-changing to enable.")
        
        print(f"Making {method} request to: {url}")
        return await self.fetcher.make_api_request(url, method, data, headers)

    async def interactive_web_research(self, topic_name: str, interactive_urls: List[str]):
        """Perform interactive research on specific URLs that require state-changing actions"""
        if not self.enable_state_changing:
            print("Warning: Interactive web research requires state-changing actions to be enabled.")
            return
        
        topic_id = self.db.get_or_create_topic(topic_name)
        print(f"Starting interactive research for '{topic_name}' on {len(interactive_urls)} URLs")
        
        tasks = []
        for url in interactive_urls:
            tasks.append(self.process_interactive_url(topic_id, url))
        
        await asyncio.gather(*tasks)

    async def process_interactive_url(self, topic_id: int, url: str):
        try:
            # Try to fetch with Selenium first
            text = await self.fetcher.fetch_with_selenium(url)
            if text:
                added, doc_id = self.db.add_document(topic_id, url, f"Interactive: {url}", text, created_at=utc_now_iso())
                if added:
                    self.db.add_snippets_from_text(topic_id, doc_id, text, created_at=utc_now_iso())
                    print(f"    -> Saved interactive content: {url}")
            else:
                print(f"    -> Failed to fetch: {url}")
        except Exception as e:
            print(f"    -> Error with {url}: {e}")
        
        await asyncio.sleep(2)  # Be respectful

    async def close(self):
        """Clean up resources"""
        if hasattr(self.fetcher, 'close'):
            await self.fetcher.close()

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

