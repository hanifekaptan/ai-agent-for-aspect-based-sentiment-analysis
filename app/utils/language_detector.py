"""
Language detection helpers.

Provides simple wrappers around `langdetect` with safe fallbacks.

Functions:
- `detect_lang(text)` -> (language_code: str, confidence: float)
- `detect_lang_safe(text)` -> dict with `language`, `confidence`, `code` keys
- `detect_lang_bulk(items)` -> list of items with `language` and `lang_confidence` set
"""
from typing import List, Dict, Tuple
import logging


try:
    from langdetect import detect_langs, DetectorFactory
    DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
except Exception:
    _HAS_LANGDETECT = False

log = logging.getLogger(__name__)

def _fallback():
    return 'und', 0.0


def detect_lang(text: str) -> Tuple[str, float]:
    """
    Returns (language_code, confidence) for the given text.

    If detection fails or the library is not available, returns ('und', 0.0).
    """
    if not text or not isinstance(text, str):
        log.debug('detect_lang called with empty/invalid text')
        return _fallback()
    if not _HAS_LANGDETECT:
        log.debug('langdetect not available, returning und')
        return _fallback()
    try:
        langs = detect_langs(text)
        if not langs:
            log.debug('detect_lang found no languages')
            return _fallback()
        top = langs[0]
        code = top.lang
        conf = float(top.prob) if hasattr(top, 'prob') else 0.0
        return code, conf
    except Exception:
        log.exception('detect_lang failed')
        return _fallback()