class UpstreamQuotaError(Exception):
    """Raised when an upstream LLM reports quota/rate-limit errors.

    This exception is used to signal the API layer to return an HTTP 429/402
    response so the frontend can disable the analyze action.
    """
    pass
