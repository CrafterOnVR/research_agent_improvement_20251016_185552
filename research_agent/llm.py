import os
import json
from typing import List

try:
    # OpenAI Python SDK v1
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


class LLMClient:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled and bool(os.getenv("OPENAI_API_KEY")) and (OpenAI is not None)
        self._client = OpenAI() if self.enabled else None
        self.model = DEFAULT_MODEL

    async def generate_questions(self, topic: str, context: str, target: int = 40) -> List[str]:
        if not self.enabled:
            return []
        prompt = (
            "You are a research assistant. Given a topic and context excerpts, produce a diverse, non-overlapping "
            f"list of about {target} specific questions that, if answered, would comprehensively cover the topic. "
            "Avoid duplicates or trivial rephrasings. Output one question per line with no numbering.\n\n"
            f"Topic: {topic}\n\nContext excerpts:\n{context}\n\nQuestions:"
        )
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            text = resp.choices[0].message.content
            lines = [l.strip("- •\t ") for l in text.splitlines() if l.strip()]
            # Dedup while preserving order
            seen = set()
            out = []
            for l in lines:
                if l.lower() in seen:
                    continue
                seen.add(l.lower())
                out.append(l)
            return out[:target]
        except Exception:
            return []

    async def summarize(self, topic: str, context: str) -> str:
        if not self.enabled:
            return f"Topic: {topic}\n(No LLM configured; showing excerpts)\n\n{context}"
        prompt = (
            "You are a careful researcher. Write a clear, structured summary of the topic using the context excerpts. "
            "Cover definitions, key ideas, applications, trade-offs, and open questions. Be concise but complete.\n\n"
            f"Topic: {topic}\n\nContext excerpts:\n{context}\n\nSummary:"
        )
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            return resp.choices[0].message.content
        except Exception:
            return f"Topic: {topic}\n(LLM summarization failed; showing excerpts)\n\n{context}"

    async def generate_tool_code(self, tool_name: str, tool_description: str) -> str:
        if not self.enabled:
            return ""
        prompt = (
            f"You are a python expert. Write a single python function called `{tool_name}` that takes a string as input and returns a string. "
            f"The function should do the following: {tool_description}. "
            f"Do not include any other text, just the python code for the function."
        )
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )
            return resp.choices[0].message.content
        except Exception:
            return ""

    async def generate_goal(self, context: str) -> dict:
        if not self.enabled:
            return {}
        prompt = (
            "You are a super-intelligent research agent. Based on the following context about your recent activities and performance, "
            "generate a single, novel, and useful goal for yourself to pursue. "
            "The goal should be something that is not in your existing list of goals. "
            "The goal should be actionable and contribute to your long-term objectives of learning, self-improvement, and knowledge discovery. "
            "Output the goal as a JSON object with the following keys: 'category', 'description', and 'priority'. "
            "The 'category' should be one of: 'learning', 'improvement', 'exploration', 'maintenance', 'creativity', 'analysis'. "
            "The 'description' should be a concise and clear description of the goal. "
            "The 'priority' should be an integer between 1 and 10. "
            "Do not add any other text, just the JSON object.\n\n"
            f"Context:\n{context}\n\nGoal:"
        )
        try:
            resp = await self._client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
            )
            text = resp.choices[0].message.content
            return json.loads(text)
        except Exception:
            return {}

