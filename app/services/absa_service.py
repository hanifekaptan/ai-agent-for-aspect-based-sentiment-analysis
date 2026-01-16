import logging
import asyncio
import time
import os
from typing import List, Dict, Any, Any as AnyType

from app.utils.errors import UpstreamQuotaError
from app.utils.parsers import parse_data, batch_packing, toon_to_dicts
from app.prompting.manager import render, normalize_items
from app.llm.client import call_llm

log = logging.getLogger(__name__)


async def analyze_items(items: AnyType, prompt_path: str = "app/prompts/absa_v1.yaml") -> Dict[str, Any]:
    """
    Analyzes items in batches with ABSA using an LLM.
    
    Args:
        items: A list of dictionaries containing 'comments' and optional 'id', 'language' keys.
        prompt_path: The name of the prompt template to use.
        
    Returns:
        A dictionary containing the results, metadata, and processing information.
        
    Raises:
        UpstreamQuotaError: If the upstream LLM returns a quota/rate limit error.
    """
    inputs = parse_data(items)
    log.info("analyze_items parsed %d inputs", len(inputs))

    batches = batch_packing(inputs, max_items=10)
    log.info("Packed %d inputs into %d batches", len(inputs), len(batches))
    
    max_concurrency = int(os.getenv("MAX_LLM_CONCURRENCY", "3"))
    per_call_timeout = int(os.getenv("LLM_TIMEOUT", "30"))
    overall_timeout = int(os.getenv("OVERALL_TIMEOUT", "60"))
    retries = int(os.getenv("LLM_RETRIES", "1"))
    backoff_base = 0.5
    
    sem = asyncio.Semaphore(max_concurrency)
    batch_results = []
    
    async def process_batch(idx: int, batch_items: List[Dict[str, Any]]) -> str:
        """Renders prompt, calls LLM with retry/backoff under a semaphore."""
        norm_items = normalize_items(batch_items)
        prompt_text = render(prompt_path, norm_items)
        model_name = os.getenv("MODEL_NAME")
        
        async with sem:
            attempt = 0
            while True:
                attempt += 1
                start_ts = time.time()
                try:
                    log.debug("Calling LLM for batch %d attempt=%d", idx, attempt)
                    response, meta = await asyncio.wait_for(
                        call_llm(prompt_text, model=model_name, timeout=per_call_timeout, retry=1, temperature=0.3),
                        timeout=per_call_timeout + 5
                    )
                    end_ts = time.time()
                    
                    log.debug("LLM returned for batch %d (len=%d)", idx, len(response))
                    return response
                    
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    msg = str(e).lower()
                    if any(k in msg for k in ("quota", "rate limit", "rate_limit", "429", "403", "quotaexceeded")):
                        log.error("Detected upstream quota/rate-limit error for batch %d: %s", idx, e)
                        raise UpstreamQuotaError(str(e))
                    
                    if attempt > retries:
                        log.exception("LLM call failed for batch %d after %d attempts", idx, attempt)
                        return f"__error__:{e}"
                    await asyncio.sleep(backoff_base * (2 ** (attempt - 1)))
    
    tasks = [asyncio.create_task(process_batch(i, b)) for i, b in enumerate(batches)]
    
    start = time.time()
    try:
        log.info("Executing %d batch tasks with max_concurrency=%d overall_timeout=%d", 
                 len(tasks), max_concurrency, overall_timeout)
        raw_responses = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True), 
            timeout=overall_timeout
        )
    except asyncio.TimeoutError:
        for t in tasks:
            if not t.done():
                t.cancel()
        raw_responses = []
        for t in tasks:
            try:
                raw_responses.append(t.result() if t.done() else "__error__:timeout")
            except Exception as e:
                raw_responses.append(f"__error__:{e}")
    
    duration = time.time() - start
    log.info("Completed processing %d batches in %.2fs", len(batches), duration)
    
    for i, r in enumerate(raw_responses):
        if isinstance(r, UpstreamQuotaError):
            log.error("UpstreamQuotaError detected in batch %d: %s", i, r)
            raise r
    
    aggregated_results = []
    for i, raw in enumerate(raw_responses):
        if isinstance(raw, Exception):
            log.warning("Batch %d returned exception: %s", i, raw)
            continue
        if raw and not raw.startswith("__error__"):
            parsed = toon_to_dicts(raw)
            log.debug("Parsed batch %d -> %d items", i, len(parsed))
            aggregated_results.extend(parsed)
        else:
            log.warning("Batch %d returned error: %s", i, raw)
    
    return {
        "items_submitted": len(inputs),
        "batches_sent": len(batches),
        "results": aggregated_results,
        "duration_seconds": duration,
    }


__all__ = ["analyze_items"]


