import asyncio
from json import dumps
from typing import Union, List

import aiohttp

# noinspection PyPep8Naming
from discord import Client as C, AutoShardedClient as AC

# noinspection PyPep8Naming
from discord.ext.commands import Bot as B, AutoShardedBot as AB
from discord.ext.tasks import loop
from ratelimit import limits, RateLimitException

from .errors import ToppyError, Forbidden, TopGGServerError, Ratelimited, NotFound
from .models import Bot, SimpleUser, BotStats
from .ratelimiter import routes

__version__ = "1.0.1"
__api_version__ = "v0"
_base_ = "https://top.gg/api"


class TopGG:
    """
    The client class for the top.gg API.

    This class handles everything for the top.gg API, APART FROM voting webhooks - Those are handled by the server
    class.
    """

    def __init__(
        self, bot: Union[C, B, AC, AB], *, token: str, autopost: bool = True, ignore_local_ratelimit: bool = False
    ):
        self.bot = bot
        self.token = token
        self.ignore_local_ratelimit = ignore_local_ratelimit
        # noinspection PyTypeChecker
        self.session = None  # type: aiohttp.ClientSession

        async def set_session():
            self.session = aiohttp.ClientSession(
                headers={
                    "User-Agent": f"top.py (version {__version__}, https://github.com/dragdev-studios/top.py)",
                    "Authorization": self.token,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )

        # Why is this here?
        # There's an undesirable warning if you make a session from outside an async function. Kinda crap but meh.
        self._session_setter = self.bot.loop.create_task(set_session())
        if autopost:
            self.autopost.start()

        # Function aliases
        self.vote_check = self.upvote_check
        self.has_upvoted = self.upvote_check
        self.get_user_vote = self.upvote_check

    def __del__(self):
        self.autopost.stop()

    async def _wf_s(self):
        if not self.session:
            await self._session_setter
        return

    @loop(minutes=30)
    async def autopost(self):
        await self.post_stats()

    async def _request(self, method: str, uri: str, **kwargs):
        if "/bots/" in uri:
            rlc = routes["/bots/*"]
            if rlc.ratelimited:
                raise Ratelimited(rlc.retry_after)
        if routes["*"].ratelimited:
            raise Ratelimited(routes["*"].retry_after)

        if kwargs.get("data") and isinstance(kwargs["data"], dict):
            kwargs["data"] = dumps(kwargs["data"])
        fail_if_timeout = kwargs.pop("fail_if_timeout", True)
        expected_codes = kwargs.pop("expected_codes", [200])
        url = _base_ + uri
        await self._wf_s()

        async with self.session.request(method, url, **kwargs) as response:
            if "application/json" not in response.headers.get("content-type", "none").lower():
                raise ToppyError("Unexpected response from server.")
            if response.status in [403, 401]:
                raise Forbidden()
            if response.status in range(500, 600):
                raise TopGGServerError()
            if response.status == 429:
                data = await response.json()
                if fail_if_timeout:
                    raise Ratelimited(data["retry-after"])
                else:
                    await asyncio.sleep(data.get("retry-after", 3600))
                    return await self._request(method, uri, **kwargs)
            if response.status == 404:
                raise NotFound()
            if response.status not in expected_codes:
                raise ToppyError("Unexpected status code '{}'".format(str(response.status)))

            data = await response.json()
            # inject metadata
            if isinstance(data, dict):
                data["_toppy_meta"] = {"headers": response.headers, "status": response.status}
        if "/bots/" in uri:
            routes["/bots/*"].add_hit()
        routes["*"].add_hit()
        return data

    async def fetch_bot(self, bot_id: int, *, fail_if_ratelimited: bool = True) -> Bot:
        """
        Fetches a bot from top.gg

        :param bot_id: The bot's client ID
        :param fail_if_ratelimited: Whether to raise an error if we get ratelimited or just wait an hour
        :return: A bot model
        """
        response = await self._request("GET", "/bots/" + str(bot_id), fail_if_timeout=fail_if_ratelimited)
        response["state"] = self.bot
        return Bot(**response)

    async def fetch_bots(
        self, limit: int = 50, offset: int = 0, search: dict = None, sort: str = None, fail_if_ratelimited: bool = True
    ) -> dict:
        limit = max(2, min(500, limit))
        uri = "/bots?limit=" + str(limit)
        if search:
            search = ", ".join(f"{x}: {y}" for x, y in search.items())
            uri += "&search=" + search
        if sort:
            uri += "&sort=" + sort
        if offset:
            uri += "&offset=" + str(offset)
        result = await self._request("GET", "/bots", fail_if_timeout=fail_if_ratelimited)
        new_results = []
        for bot in result["results"]:
            bot["state"] = self.bot
            new_results.append(Bot(**bot))
        result["results"] = new_results
        return result

    async def bulk_fetch_bots(self, limit: int = 500, *args) -> dict:
        """Similar to fetch_bots, except allows for requesting more than 500.

        This is equivalent to:
        ```python
        batch_one = await TopGG.fetch_bots(500)
        batch_two = await TopGG.fetch_bots(500, offset=500)
        batch_three = await TopGG.fetch_bots(500, offset=1000)
        ...
        ```
        """
        results = {}
        remaining = limit
        for i in range(0, limit, 500):
            amount = min(500, remaining)
            batch_results = await self.fetch_bots(amount, offset=i, *args)
            remaining -= amount
            results = {**results, **batch_results}
        return results

    async def fetch_votes(self, *, fail_if_ratelimited: bool = True) -> List[SimpleUser]:
        """Fetches the last 1000 voters for your bot."""
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        raw_users = await self._request("GET", f"/bots/{self.bot.user.id}/votes", fail_if_timeout=fail_if_ratelimited)
        resolved = list(map(lambda u: SimpleUser(**u), raw_users))
        return resolved

    async def upvote_check(self, user_id: int, *, fail_if_ratelimited: bool = True) -> bool:
        """Checks to see if the provided user has voted for your bot in the pas 12 hours."""
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        uri = f"/bots/{self.bot.user.id}/check?userId={user_id}"
        raw_users = await self._request("GET", uri, fail_if_timeout=fail_if_ratelimited)
        return raw_users["voted"] == 1

    async def get_stats(self, bot_id: int, *, fail_if_ratelimited: bool = True) -> BotStats:
        """Fetches the server & shard count for a bot.

        NOTE: this does NOT fetch votes. Use the fetch_bot function for that."""
        uri = f"/bots/{bot_id}/stats"
        raw_stats = await self._request("GET", uri, fail_if_timeout=fail_if_ratelimited)
        return BotStats(**raw_stats)

    async def post_stats(self, stats: dict = None, *, fail_if_ratelimited: bool = True) -> int:
        """
        Posts your bot's current statistics to top.gg

        :param stats: Use these stats instead of auto-generated ones. Not recommended.
        :param fail_if_ratelimited: Whether to raise an error if ratelimited or wait an hour
        :return: an integer of how many servers got posted.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        override = stats is not None
        stats = stats or {}
        if not override:
            stats["server_count"] = len(self.bot.guilds)
            if hasattr(self.bot, "shards") and self.bot.shards:
                shards = []
                for shard in self.bot.shards.values():
                    shards.append(len([x for x in self.bot.guilds if x.shard_id == shard.id]))
                stats["shards"] = shards
                stats["shard_count"] = self.bot.shard_count

        await self._request(
            "POST", f"/bots/{self.bot.user.id}/stats", data=dumps(stats), fail_if_timeout=fail_if_ratelimited
        )
        return stats["server_count"]

    async def is_weekend(self) -> bool:
        """Returns True or False, depending on if it's a "weekend".

        If it's a weekend, votes count as double."""
        data = await self._request("GET", f"/weekend")
        return data["is_weekend"]
