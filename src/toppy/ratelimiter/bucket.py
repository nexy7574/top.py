import logging
from datetime import datetime, timedelta, timezone
from typing import Dict

logger = logging.getLogger(__name__)


class Ratelimit:
    r"""
    Internalised ratelimit class to prevent 429s from top.gg

    :param route: str - Not actually used.
    :param max_hits: int - The maximum number of times the API can be hit before a 429 is expected.
    :param cooldown: float - The ratelimit period in seconds.
    """

    def __init__(self, route: str, max_hits: int, per: int, cooldown: float):
        self.route = route
        self.max_hits = max_hits
        self.__hits = 0
        self.cooldown = cooldown
        self.per = per
        self.expires = datetime.min.replace(tzinfo=timezone.utc)
        self.calls = []

    def __repr__(self):
        return ("<Ratelimit route={0.route!r} hits={0.hits!r} max_hits={0.max_hits!r} per={0.per!r} "
                "cooldown={0.cooldown!r} expires={0.expires!r} ratelimited={0.ratelimited!r} "
                "retry_after={0.retry_after!r}>").format(self)

    @property
    def hits(self) -> int:
        return self.__hits

    @property
    def ratelimited(self) -> bool:
        r"""
        Boolean indicating if the current route is ratelimited.
        :return: True if a request would become ratelimited, otherwise False.
        """
        now = datetime.now(tz=timezone.utc)
        if now > self.expires:
            self.reset()
        return self.hits >= self.max_hits

    def reset(self):
        self.__hits = 0
        self.expires = datetime.min.replace(tzinfo=timezone.utc)

    @property
    def retry_after(self) -> float:
        r"""
        Floating point number indicating how long, in seconds, until the current ratelimit has expired.

        .. Note::
            This function ALWAYS returns a float. This means ``0.0`` will be returned if there's no ratelimit active.

        :return: How long (in seconds) until the current ratelimit is over.
        """
        if not self.expires:
            return 0.0
        if self.hits < self.max_hits:
            return 0.0
        return max((self.expires - datetime.now(tz=timezone.utc)).total_seconds(), 0.0)

    def sync_from_ratelimit(self, retry_after: float = 3600.0):
        r"""
        Syncs the internal ratelimit clock to that of a 429 response.

        :param retry_after: float - The retry_after value
        """
        self.reset()
        self.__hits = self.max_hits
        self.cooldown = retry_after
        self.expires = datetime.now(tz=timezone.utc) + timedelta(seconds=retry_after)

    def add_hit(self):
        r"""Handles adding a hit to the route and dealing with the datetime-y stuff"""
        if self.expires is None or self.expires <= datetime.now(tz=timezone.utc):
            self.reset()
            self.expires = datetime.now(tz=timezone.utc) + timedelta(seconds=self.per)
        self.__hits += 1
