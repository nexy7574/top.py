class ToppyError(Exception):
    """
    The base exception for all top.py errors.
    This exception is inherited from Exception.
    You could use this as a catchall error for all errors from the module. For example

    .. code:: python

        try:
            await toppy.broken_function()
        except toppy.ToppyError:
            print("Error")

    """


class Forbidden(ToppyError):
    """
    Raised whenever a request was rejected due to a lack of correct authentication.
    Authentication can occur if:

    * You provided an old, expired API Token
    * You have been banned from the top.gg API
    """


class Ratelimited(ToppyError):
    """
    Raised whenever the client is ratelimited for a long time and refused to handle it.


    internal: bool - Boolean indicating if the ratelimit was raised by the precautionary internal ratelimit handler
    retry_after: float - How long, in seconds, until the ratelimit is lifted.
    __str__: str - A nicely formatted message describing this error
    """

    def __init__(self, retry_after: float = 0.0, *, internal: bool = False):
        self.internal = internal
        self.retry_after = retry_after

    def __str__(self):
        who = "internal ratelimiter" if self.internal else "top.gg API"
        return f"Ratelimited by the {who} - Retry after " + str(self.retry_after) + "s"


class NotFound(ToppyError):
    """
    Raised when a requested resource is not found.
    """


class TopGGServerError(ToppyError):
    """Raised whenever the client encounters a 5xx status"""
