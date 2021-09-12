from datetime import datetime, timedelta
from typing import Dict


class Ratelimit:
    r"""
    Internalised ratelimit class to prevent 429s from top.gg

    :param route: str - Not actually used.
    :param hits: int - The maximum number of times the API can be hit before a 429 is expected.
    :param cooldown: float - The cooldown time when hitting a 429. For top.gg, this is always 3600.0 (1 hour)
    """

    def __init__(self, *, route: str, hits: int, cooldown: float):
        self.route = route
        self.max_hits = hits
        self.hits = 0
        self.cooldown = cooldown
        self.expires = datetime.min
        self.calls = []

    @property
    def ratelimited(self) -> bool:
        r"""
        Boolean indicating if the current route is ratelimited.
        :return: True if a request would become ratelimited, otherwise False.
        """
        return self.hits >= self.max_hits and datetime.utcnow() <= self.expires

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
        return max((self.expires - datetime.utcnow()).total_seconds(), 0.0)

    def sync_from_ratelimit(self, retry_after: float):
        r"""
        Syncs the internal ratelimit clock to that of a 429 response.

        :param retry_after: float - The retry_after value
        """
        self.hits = self.max_hits
        self.cooldown = retry_after
        self.expires = datetime.utcnow() + timedelta(seconds=retry_after)

    def add_hit(self):
        r"""Handles adding a hit to the route and dealing with the datetime-y stuff"""
        self.hits += 1
        if self.expires is None or self.expires <= datetime.utcnow():
            self.expires = datetime.utcnow() + timedelta(seconds=self.cooldown)


_routes: Dict[str, Ratelimit] = {
    "*": Ratelimit(route="*", hits=100, cooldown=3600),
    "/bots/*": Ratelimit(route="/bots/*", hits=60, cooldown=3600),
}
