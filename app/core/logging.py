import logging
import time
from typing import Dict, Any, Callable, List

_TOKEN_REPORTS: List[Dict[str, Any]] = []


def init_logging(level: int = logging.INFO):
    class RequestIdFilter(logging.Filter):
        def filter(self, record):
            if not hasattr(record, 'request_id'):
                record.request_id = '-'
            return True

    fmt = '%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s'
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(level)


__all__ = ['init_logging']
