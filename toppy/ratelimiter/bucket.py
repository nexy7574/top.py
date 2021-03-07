from datetime import datetime, timedelta


class Ratelimit:
    def __init__(self, *, route: str, hits: int, cooldown: float):
        self.route = route
        self.max_hits = hits
        self.hits = 0
        self.cooldown = cooldown
        self.expires = datetime.min

    @property
    def ratelimited(self):
        return self.hits >= self.max_hits and datetime.utcnow() <= self.expires

    @property
    def retry_after(self):
        if not self.expires:
            return 0.0
        return max((self.expires - datetime.utcnow()).total_seconds(), 0.0)

    def add_hit(self):
        self.hits += 1
        if self.expires is None or self.expires <= datetime.utcnow():
            self.expires = datetime.utcnow() + timedelta(seconds=self.cooldown)


_routes = {
    "*": Ratelimit(route="*", hits=100, cooldown=3600),
    "/bots/*": Ratelimit(route="/bots/*", hits=60, cooldown=3600)
}
