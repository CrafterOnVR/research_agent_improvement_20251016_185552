from typing import Dict, Iterable

try:
    # duckduckgo_search v5+
    from duckduckgo_search import DDGS  # type: ignore
except Exception:  # pragma: no cover
    DDGS = None  # fallback handled below


class Searcher:
    def __init__(self, max_results: int = 10):
        self.max_results = max_results

    def search(self, query: str) -> Iterable[Dict]:
        if DDGS is None:
            return []
        try:
            with DDGS(timeout=15) as ddgs:
                for r in ddgs.text(query, max_results=self.max_results, region="wt-wt", safesearch="Moderate"):
                    yield r
        except Exception:
            return []

