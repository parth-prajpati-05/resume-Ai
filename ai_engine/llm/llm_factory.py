"""
LLM Factory — Abstraction layer supporting HuggingFace, OpenAI, and Gemini
Defaults to HuggingFace Inference API with Mistral-7B
"""

from typing import Optional
from loguru import logger
from backend.core.config import settings


class LLMFactory:
    """
    Abstract LLM interface. Supports:
    - huggingface (default, free tier)
    - openai
    - gemini
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or settings.LLM_PROVIDER
        self._llm = None
        self._init_llm()

    def _init_llm(self):
        if self.provider == "huggingface":
            self._init_huggingface()
        elif self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def _init_huggingface(self):
        try:
            from langchain_huggingface import HuggingFaceEndpoint

            self._llm = HuggingFaceEndpoint(
                repo_id=settings.HF_LLM_MODEL,
                huggingfacehub_api_token=settings.HUGGINGFACE_API_KEY,
                max_new_tokens=512,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.1,
                task="text-generation",
            )
            logger.info(f"✅ HuggingFace LLM initialized: {settings.HF_LLM_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to init HuggingFace LLM: {e}")
            self._llm = None

    def _init_openai(self):
        try:
            from langchain_openai import ChatOpenAI

            self._llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-3.5-turbo",
                temperature=0.3,
                max_tokens=512,
            )
            logger.info("✅ OpenAI LLM initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init OpenAI LLM: {e}")
            self._llm = None

    def _init_gemini(self):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI

            self._llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=0.3,
                max_output_tokens=512,
            )
            logger.info("✅ Gemini LLM initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init Gemini LLM: {e}")
            self._llm = None

    def get_llm(self):
        return self._llm

    def invoke(self, prompt: str) -> str:
        """Invoke LLM with a prompt string and return response text."""
        if self._llm is None:
            logger.warning("⚠️ LLM not initialized, returning empty response")
            return ""
        try:
            response = self._llm.invoke(prompt)
            if hasattr(response, "content"):
                return response.content.strip()
            return str(response).strip()
        except Exception as e:
            logger.error(f"❌ LLM invocation failed: {e}")
            return f"[LLM Error: {str(e)}]"


# Singleton instance
_llm_instance: Optional[LLMFactory] = None


def get_llm_factory() -> LLMFactory:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMFactory()
    return _llm_instance
