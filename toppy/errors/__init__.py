class ToppyError(Exception):
    """The base exception for all top.py errors."""


class Forbidden(ToppyError):
    """Raised whenever a request was rejected due to unauthorization."""


class Ratelimited(ToppyError):
    """Raised whenever the client is ratelimited for a long time and refused to handle it."""

    def __init__(self, retry_after: float = 0.0, *, internal: bool = False):
        self.internal = internal
        self.retry_after = retry_after

    def __str__(self):
        who = "internal ratelimiter" if self.internal else "top.gg API"
        return f"Ratelimited by the {who} - Retry after " + str(self.retry_after) + "s"


class NotFound(ToppyError):
    """Raised when a requested endpoint is not found."""


class TopGGServerError(ToppyError):
    """Raised whenever the client encounters a 5xx status"""
