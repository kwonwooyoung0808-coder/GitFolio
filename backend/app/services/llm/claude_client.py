import anthropic
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.exceptions import LLMError


class ClaudeClient:
    def __init__(self):
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

    async def generate(self, prompt: str) -> str:
        if not settings.ANTHROPIC_API_KEY:
            raise LLMError("Anthropic API key is not configured.")

        try:
            response = await self.anthropic_client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=2200,
                messages=[{"role": "user", "content": prompt}],
            )
        except Exception as exc:
            raise LLMError(str(exc)) from exc

        chunks = []
        for block in response.content:
            text = getattr(block, "text", "")
            if text:
                chunks.append(text)
        return "".join(chunks).strip()

    async def _stream_anthropic(self, prompt: str):
        async with self.anthropic_client.messages.stream(
            model=settings.CLAUDE_MODEL,
            max_tokens=2200,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            async for text in stream.text_stream:
                yield text

    async def _stream_openai(self, prompt: str):
        if not self.openai_client:
            raise LLMError("Claude failed and OpenAI fallback is not configured.")

        stream = await self.openai_client.chat.completions.create(
            model=settings.OPENAI_FALLBACK_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta

    async def stream(self, prompt: str):
        try:
            async for text in self._stream_anthropic(prompt):
                yield {"source": "claude", "text": text}
            return
        except Exception:
            if not settings.OPENAI_API_KEY:
                raise

        try:
            async for text in self._stream_openai(prompt):
                yield {"source": "openai", "text": text}
        except Exception as exc:
            raise LLMError(str(exc)) from exc
