import asyncio
import os
import logging
import time
from typing import Optional, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

log = logging.getLogger(__name__)

_llm_client = None
_llm_model_name = None


def _init_llm(model_name: str, api_key: str, temperature: float, max_output_tokens: int):
    global _llm_client, _llm_model_name
    if _llm_client is None or _llm_model_name != model_name:
        try:
            _llm_client = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
            )
            _llm_model_name = model_name
            log.info("LLM client initialized with model: %s", model_name)
        except Exception as e:
            log.exception("Failed to initialize ChatGoogleGenerativeAI")
            raise ValueError(f"Error initializing LLM client: {e}") from e
    return _llm_client


async def call_llm(
    prompt: str,
    model: Optional[str] = None,
    timeout: int = 30,
    retry: int = 1,
    temperature: float = 0.1,
    max_output_tokens: int = 8192,
) -> tuple[str, Dict[str, Any]]:
    """
    Invokes the Gemini model with a given prompt.

    Args:
        prompt (str): The prompt to send to the model.
        model (Optional[str]): The name of the model to use.
        timeout (int): Timeout for the request.
        retry (int): Number of retries for failed attempts.
        temperature (float): Controls the randomness of the model's output.
        max_output_tokens (int): The maximum number of tokens the model will generate.

    Returns:
        A tuple: (response text, metadata dictionary).

    Raises:
        ValueError: If required environment variables are not set.
        RuntimeError: If the LLM call fails.
    """
    api_key = os.environ.get('GOOGLE_API_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY environment variable is required. "
            "Please set it in your .env file or environment."
        )

    model_name = model or os.environ.get('MODEL_NAME')
    llm = _init_llm(model_name, api_key, temperature, max_output_tokens)

    def _sync_call() -> tuple[str, Dict[str, Any]]:
        try:
            log.debug("Sending prompt to %s (length: %d chars)", model_name, len(prompt))
            response = llm.invoke(prompt)
            if isinstance(response, str):
                result = response
            elif hasattr(response, 'content'):
                result = str(response.content)
            elif hasattr(response, 'text'):
                result = str(response.text)
            else:
                result = str(response)
            log.debug("Received response (length: %d chars)", len(result))
            return result, {}
        except Exception:
            log.exception("LLM call failed")
            raise

    last_error = None
    result = None
    token_usage: Dict[str, Any] = {}
    for attempt in range(1, retry + 1):
        try:
            result, token_usage = await asyncio.to_thread(_sync_call)
            break
        except Exception as e:
            last_error = e
            if attempt < retry:
                log.warning("LLM call attempt %d failed, retrying...", attempt)
                await asyncio.sleep(1 * attempt)
            else:
                log.error("LLM call failed after %d attempts", retry)

    if result is None:
        raise last_error or RuntimeError("LLM call failed")

    return result, {}

__all__ = ['call_llm']
