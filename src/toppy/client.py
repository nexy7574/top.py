import logging
import warnings
from json import dumps
from typing import TYPE_CHECKING, List, Optional, Union
from importlib.metadata import version

import aiohttp
import discord
from discord.ext.tasks import loop

from .errors import Forbidden, NotFound, Ratelimited, TopGGServerError, ToppyError
from .ratelimiter import Ratelimit
from .models import (
    Bot,
    BotSearchResult,
    Last1000VotesResponse,
    VoteResult,
    IndividualUserVoteResult,
    BotStatsResult,
    BotStatsPayload,
    User
)

# noinspection PyPep8Naming

if TYPE_CHECKING:
    from discord import Client as DiscordClient

logger = logging.getLogger(__name__)

__VERSION__ = version("top.py")


class BulkFetchBotsIterator:
    def __init__(
            self,
            limit: int = 50,
            offset: int = 0,
            search: dict = None,
            sort: str = None,
            *,
            state: "TopGG"
    ):
        self.limit = limit
        self.offset = offset
        self.search = search
        self.sort = sort
        self._state = state

    def __aiter__(self) -> "BulkFetchBotsIterator":
        return self

    async def __anext__(self) -> BotSearchResult:
        if not self._state.session:
            raise StopAsyncIteration("Session not initialized.")
        r = await self._state.fetch_bots(
            limit=self.limit,
            offset=self.offset,
            search=self.search,
            sort=self.sort
        )
        if r.count == 0:
            raise StopAsyncIteration
        self.offset += r.count
        return r

    async def flatten(self) -> BotSearchResult:
        r"""Flattens the iterator into a single BotSearchResult."""
        results = []
        async for x in self:
            x: BotSearchResult
            results.extend(x.results)
        return BotSearchResult(*results, limit=self.limit, offset=self.offset, count=len(results), total=len(results))


class TopGG:
    """
    The client class for the top.gg API.

    This class handles everything for the top.gg API, APART FROM voting webhooks - Those are handled by the server
    class.
    """
    __api_version__ = "v0"
    _base_ = "https://top.gg/api"

    def __init__(self, bot: "DiscordClient", *, token: str, autopost: bool = True):
        self.bot = bot
        self.token = token
        self.ratelimit_persistence = True
        # noinspection PyTypeChecker
        self._session: Optional[aiohttp.ClientSession] = None
        if autopost:
            logger.debug("Starting autopost task.")
            self.autopost.start()

        # Function aliases
        self.vote_check = self.upvote_check
        self.has_upvoted = self.upvote_check
        self.get_user_vote = self.upvote_check

        self.ratelimits = {
            "/bots/*": Ratelimit(route="/bots/*", max_hits=60, per=60, cooldown=3600),
            "*": Ratelimit(route="*", max_hits=120, per=60, cooldown=3600)
        }

    def _change_api_version(self, v: int):
        # You shouldn't use this unless v1 is released, and you MUST use it before the package catches up.
        # If you change the API version then there is no guarantee that literally anything will work.
        warnings.warn(UserWarning("You changed the API version. functionality is not a guarantee."))
        # I actually have no idea how they'll handle the API version change, so we're just gonna
        # append the version string
        self.__api_version__ = "v" + str(v)
        self._base_ += self.__api_version__

    def __del__(self):
        r"""Lower-level garbage collection function fired when the variable is discarded, performs cleanup."""
        logger.debug(f"{id(self)} __del__ called - Stopping autopost task")
        self.autopost.stop()

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        r"""
        Returns the current top.py client session.

        .. warning::
            You must have at least called one function before using this variable, as the connection is not created
            on class initialization.

        :return: The current aiohttp client session
        :rtype: :class:`http:aiohttp.ClientSession`
        """
        return self._session

    @property
    def vote_url(self) -> str:
        r"""
        Just gives you a link to your bot's vote page.

        :rtype: :class:`py:str`
        """
        if not self.bot.is_ready():
            raise TypeError("Bot is not ready, can't produce a vote URL.")
        return f"https://top.gg/bot/{self.bot.user.id}/vote"

    @property
    def invite_url(self) -> str:
        r"""Just gives you a link to your bot's invite page."""
        if not self.bot.is_ready():
            raise TypeError("Bot is not ready, can't produce an invite URL.")
        return f"https://top.gg/bot/{self.bot.user.id}/invite"

    async def _wf_s(self):
        if not self.session:
            self._session = aiohttp.ClientSession(
                headers={
                    "User-Agent": f"top.py (version {__VERSION__}, https://github.com/nexy7574/top.py)",
                    "Authorization": self.token,
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
            )
        return

    @loop(minutes=30)
    async def autopost(self):
        r"""The task that automatically posts our stats to top.gg."""
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        result = await self.post_stats()
        self.bot.dispatch("toppy_stat_autopost", result)

    async def _request(self, method: str, uri: str, **kwargs) -> dict:
        logging.warning(f"Requesting {method} {uri} with kwargs {kwargs}")
        if "/bots/" in uri:
            rlc = self.ratelimits["/bots/*"]
            if rlc.ratelimited:
                logger.warning(f"Ratelimted for {rlc.retry_after*1000:,}ms. Handled under the bucket /bots/*.")
                raise Ratelimited(rlc.retry_after, limiter=rlc, internal=True)
        if self.ratelimits["*"].ratelimited:
            logger.warning(
                f"Ratelimited for {self.ratelimits['*'].retry_after*1000:,}ms. Handled under the bucket /*."
                f" Perhaps review how many requests you're sending?"
            )
            raise Ratelimited(self.ratelimits["*"].retry_after, limiter=self.ratelimits["*"], internal=True)

        if kwargs.get("data") and isinstance(kwargs["data"], dict):
            kwargs["data"] = dumps(kwargs["data"])

        expected_codes = kwargs.pop("expected_codes", [200])
        url = self._base_ + uri
        await self._wf_s()

        logger.info('Sending "{} {}"...'.format(method, url))
        async with self.session.request(method, url, **kwargs) as response:
            if response.status in range(500, 600):
                raise TopGGServerError()
            else:
                self.bot.dispatch("toppy_request", url=url, method=method)
                # NOTE: This has moved from just before the return since the hits count as soon as a response
                # is generated (unless it's 5xx).
                if "/bots/" in uri:
                    self.ratelimits["/bots/*"].add_hit()
                self.ratelimits["*"].add_hit()

            if "application/json" not in response.headers.get("content-type", "none").lower():
                logger.warning(f"Got unexpected content type {response.headers['Content-Type']!r} from top.gg.")
                raise ToppyError("Unexpected response from server.")
            if response.status in [403, 401]:
                raise Forbidden()
            if response.status == 429:
                logging.warning("Unexpected ratelimit. Re-syncing internal ratelimit handler.")
                data = await response.json()
                if "/bots/" in uri:
                    self.ratelimits["/bots/*"].sync_from_ratelimit(data["retry-after"])
                self.ratelimits["*"].sync_from_ratelimit(data["retry-after"])

                # NOTE: This is a bit of a whack way to deal with this.
                # There should definitely be only one way to handle a ratelimit
                # however not every user wants to handle an exception.
                # We'll keep this for now, however it will definitely change when top.gg releases v[1|2] of their
                # API.
                raise Ratelimited(data["retry-after"])
            if response.status == 404:
                raise NotFound()
            if response.status not in expected_codes:
                raise ToppyError("Unexpected status code '{}'".format(str(response.status)))

            data = await response.json()
            # inject metadata
            if isinstance(data, dict):
                data["_toppy_meta"] = {"headers": response.headers, "status": response.status}
        return data

    async def fetch_bot(self, bot: Union[discord.User, discord.Member, discord.Object]) -> Bot:
        r"""
        Fetches a bot from top.gg

        :param bot: The bot's user to fetch
        :type bot: Union[:class:`discord:discord.User`, :class:`discord:discord.Member`]
        :return: The retrieved bot
        :rtype: :class:`toppy.models.Bot`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.Forbidden: You didn't specify a valid API token, or you are banned from the API.
        :raises toppy.errors.NotFound: The specified bot is not on top.gg.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        response = await self._request("GET", "/bots/" + str(bot.id))
        response["state"] = self.bot
        logger.debug(f"Response from fetch_bot: {response}")
        return Bot(**response)

    async def fetch_bots(
        self, limit: int = 50, offset: int = 0, search: dict = None, sort: str = None
    ) -> BotSearchResult:
        r"""
        Fetches up to ``limit`` bots from top.gg

        :param limit: How many bots to fetch.
        :param offset: How many bots to "skip" (pagination)
        :param search: Search pairs (e.g. {"library": "discord.py"})
        :param sort: What field to sort by. Prefix with dash to reverse results.
        :type limit: :class:`py:int`
        :type offset: :class:`py:int`
        :type search: Optional[:class:`py:dict`]
        :type sort: Optional[:class:`py:str`]
        :return: The results of your search (up to ``limit`` results)
        :rtype: :class:`toppy.models.BotSearchResults`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.Forbidden: You didn't specify a valid API token, or you are banned from the API.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        limit = max(2, min(500, limit))
        uri = "/bots?limit=" + str(limit)
        if search:
            search = ", ".join(f"{x}: {y}" for x, y in search.items())
            uri += "&search=" + search
        if sort:
            uri += "&sort=" + sort
        if offset:
            uri += "&offset=" + str(offset)
        result = await self._request("GET", "/bots")
        logger.debug(f"Response from fetching bots: {result}")
        new_results = []
        for bot in result.pop("results"):
            bot["state"] = self.bot
            new_results.append(Bot(**bot))
        return BotSearchResult(results=new_results, **result)

    def bulk_fetch_bots(
            self,
            limit: int = 500,
            offset: int = 0,
            search: dict = None,
            sort: str = None
    ) -> BulkFetchBotsIterator:
        r"""Similar to fetch_bots, except allows for requesting more than 500 bots at once.

        .. warning::

            This function is not guaranteed to return *exactly* ``limit``.

            Keep in mind that it returns *up to* ``limit``

        .. danger::

            Since this function sends multiple requests, it can take a long time.

            Furthermore, sending a bulk request for more than thirty thousand (30,000) bots will cause you to be
            ratelimited.

        This is equivalent to: ::

            batch_one = await TopGG.fetch_bots(500)
            batch_two = await TopGG.fetch_bots(500, offset=500)
            batch_three = await TopGG.fetch_bots(500, offset=1000)

        :param limit: How many bots to fetch.
        :param offset: How many bots to "skip" (pagination)
        :param search: Search pairs (e.g. {"library": "discord.py"})
        :param sort: What field to sort by. Prefix with dash to reverse results.
        :type limit: :class:`py:int`
        :type offset: :class:`py:int`
        :type search: Optional[:class:`py:dict`]
        :type sort: Optional[:class:`py:str`]
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.Forbidden: You didn't specify a valid API token, or you are banned from the API.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if limit > 30_000:
            raise ValueError("Cannot process more than 30 thousand bots at once (definite ratelimit)")
        return BulkFetchBotsIterator(limit=limit, offset=offset, search=search, sort=sort, state=self)

    async def fetch_votes(self) -> Last1000VotesResponse:
        r"""
        Fetches the last 1000 voters for your bot.

        :returns: A list of up to 1000 SimpleUser objects who have voted for your bot in the past (any time period).
        :rtype: :class:`py:list` [:class:`toppy.models.SimpleUser`]
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        raw_users = await self._request("GET", f"/bots/{self.bot.user.id}/votes")
        logger.debug(f"Response from fetching votes: {raw_users}")
        return [VoteResult(**x) for x in raw_users]

    async def upvote_check(self, user: Union[discord.User, discord.Member, discord.Object]) -> IndividualUserVoteResult:
        r"""
        Checks to see if the provided user has voted for your bot in the pas 12 hours.

        :param user: The user to fetch upvote for.
        :returns: True if the has user voted in the past 12 hours, False if not
        :rtype: :class:`IndividualUserVoteResult`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        uri = f"/bots/{self.bot.user.id}/check?userId={user.id}"
        raw_result = await self._request("GET", uri)
        logger.debug(f"Response from fetching upvote check: {raw_result}")
        # Ah yes, three pieces of recycled code. How cool.
        return IndividualUserVoteResult(**raw_result)

    async def get_stats(self, bot: Union[discord.User, discord.Member, discord.Object]) -> BotStatsResult:
        r"""Fetches the server & shard count for a bot.

        NOTE: this does NOT fetch votes. Use the fetch_bot function for that.

        :returns: Basic statistics on the specified bot.
        :rtype: :class:`toppy.models.BotStats`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code
        was given.
        """
        uri = f"/bots/{bot.id}/stats"
        raw_stats = await self._request("GET", uri)
        logger.debug(f"Response from fetching stats: {raw_stats}")
        return BotStatsResult(**raw_stats)

    async def post_stats(self, force_shard_count: bool = False) -> BotStatsPayload:
        r"""
        Posts your bot's current statistics to top.gg

        :type force_shard_count: :class:`py:bool`
        :param force_shard_count: If true, always include shard data, even when it would normally be excluded

        :returns: an integer of how many servers got posted.
        :rtype: :class:`BotStatsResult`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        stats = {"server_count": len(self.bot.guilds)}
        if (hasattr(self.bot, "shards") and self.bot.shards) or force_shard_count is True:
            shards = []
            for shard in self.bot.shards.values():
                shards.append(len([x for x in self.bot.guilds if x.shard_id == shard.id]))
            stats["shards"] = shards
            stats["shard_count"] = max(self.bot.shard_count, 1)
            stats["shard_id"] = self.bot.shard_id or 0

        response = await self._request("POST", f"/bots/{self.bot.user.id}/stats", data=dumps(stats))
        logger.debug(f"Response from fetching posting stats: {response}")
        self.bot.dispatch("guild_post", stats)
        return BotStatsPayload(**response)

    # async def is_weekend(self) -> bool:
    #     r"""Returns True or False, depending on if it's a "weekend".
    #
    #     If it's a weekend, votes count as double.
    #
    #     :rtype: :class:`py:bool:`
    #     data = await self._request("GET", f"/weekend")
    #     return data["is_weekend"]

    # /weekend is no-longer documented(?)

    async def fetch_user(self, user: Union[discord.User, discord.Member, discord.Object]) -> User:
        """
        Fetches a user's profile from top.gg.

        :param user: Union[discord.User, discord.Member] - Who's top.gg profile to fetch.
        :raises toppy.errors.Forbidden: - Your API token was invalid.
        :raises toppy.errors.NotFound: - The user who you requested does not have a top.gg profile.
        :returns toppy.models.User: The fetched user's profile
        """
        data = await self._request("GET", f"/users/{user.id}")
        return User(**data)
