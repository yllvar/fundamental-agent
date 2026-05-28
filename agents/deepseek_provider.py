import os
import logging
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"

class DeepSeekProvider:
    """DeepSeek API provider — drop-in replacement for ChatBedrock/LLM interface.
    Provides both async (ainvoke) and sync (invoke) methods matching the patterns
    used across the codebase (call_llm in strands, invoke_llm in legacy agents).
    """
    def __init__(self, model: str = DEFAULT_MODEL, temperature: float = 0.7, max_tokens: int = 4000):
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            logger.warning("DEEPSEEK_API_KEY not set — LLM calls will fail")
        self.api_key = api_key or ""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._async_client: AsyncOpenAI | None = None
        self._sync_client: OpenAI | None = None

    @property
    def async_client(self) -> AsyncOpenAI:
        if self._async_client is None:
            self._async_client = AsyncOpenAI(api_key=self.api_key, base_url=DEEPSEEK_BASE_URL)
        return self._async_client

    @property
    def sync_client(self) -> OpenAI:
        if self._sync_client is None:
            self._sync_client = OpenAI(api_key=self.api_key, base_url=DEEPSEEK_BASE_URL)
        return self._sync_client

    async def ainvoke(self, system_prompt: str, user_prompt: str) -> str:
        """Async call matching BaseStrandAgent.call_llm() interface."""
        response = await self.async_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""

    def invoke(self, messages: list[dict[str, str]]) -> str:
        """Sync call matching BaseAgent.invoke_llm() interface.
        messages: [{"role": "system"|"user"|"assistant", "content": str}, ...]
        """
        response = self.sync_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""

    @property
    def available(self) -> bool:
        return bool(self.api_key)
