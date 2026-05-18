import httpx

from app.core.config import settings
from app.core.exceptions import LLMError


class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def generate(self, prompt: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.2,
                        },
                    },
                )
                response.raise_for_status()
                data = response.json()
                text = (data.get("response") or "").strip()
                if not text:
                    raise LLMError("Ollama returned an empty response.")
                return text
        except Exception as exc:
            raise LLMError(f"Ollama request failed: {exc}") from exc
