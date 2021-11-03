import logging
import traceback
import warnings
from json import dumps
from typing import Union, List, Optional, Callable, Any

import aiohttp
import discord
from discord import Client
from discord.ext.tasks import loop

from .errors import ToppyError, Forbidden, TopGGServerError, Ratelimited, NotFound
from .models import Bot, SimpleUser, BotStats, User, BotSearchResults
from .ratelimiter import routes

__version__ = "2.0.0dev1"
__api_version__ = "v0"
_base_ = "https://top.gg/api"
logger = logging.getLogger(__name__)


class TopGG:
    r"""
    Handles and processes all the transactions between your code and top.gg's API.

    **Parameters:**

        bot: :obj:`discord.Client`
            The bot instance to use. Can be client or bot, and their auto-sharded equivalents.
        token: :obj:`py:str`
            Your bot's API token from top.gg.
        autopost: :obj:`py:bool`
            Whether to automatically post server count every 30 minutes or not.
        event_callback: :obj:`Optional[Callable[[str, Optional[Any], Optional[Any]], Any]]`
            The function to use when dispatching any of the events used in this library (see: event reference).
            The only guaranteed argument is the event name, which is the first argument provided.
            Any argument after that is dependant on what the event provides.

            .. warning::
                If this option is not overridden, it will default to ``bot.dispatch``, which some discord.py forks
                may not have.

            Example:

            .. code-block::

                # python 3.10
                from toppy.client import TopGG

                async def on_toppy_event(event_name, *args):
                    match event_name:
                        case "toppy_request":
                            print("top.py sent a %s request to %s." % args)
                        case "guild_post":
                            print("Posted server count:", args[0]["server_count"]
                        case _:
                            print("Unhandled event:", event_name)

                client = TopGG(..., event_callback=on_toppy_event)
    """
    # TODO: Fix that title in the docstring

    def __init__(self, bot: Client, *, token: str, autopost: bool = True,
                 event_callback: Optional[Callable[[str, Optional[Any], Optional[Any]], Any]] = ...):
        self.bot = bot
        self.token = token
        self._callback = event_callback
        if self._callback is ...:
            if hasattr(self.bot, "dispatch"):
                self._callback = self.bot.dispatch
            else:
                def no_op(*args):
                    return args  # the callback is never checked on our end

                self._callback = no_op
                warnings.warn("No valid callback found - defaulting to no-op")

        # noinspection PyTypeChecker
        self._session: Optional[aiohttp.ClientSession] = None
        if autopost:
            self.autopost.start()

        # Function aliases
        self.vote_check = self.upvote_check
        self.has_upvoted = self.upvote_check
        self.get_user_vote = self.upvote_check

    def __del__(self):
        self.autopost.stop()
    
    async def callback(self, event_name, *args):
        try:
            await discord.utils.maybe_coroutine(self._callback, event_name, *args)
        except Exception as e:
            print("Ignoring exception in top.py callback function:")
            traceback.print_exception(type(e), e, e.__traceback__)
        finally:
            return

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
                    "User-Agent": f"top.py (version {__version__}, https://github.com/dragdev-studios/top.py)",
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
        await self.callback("toppy_stat_autopost", result)

    async def _request(self, method: str, uri: str, **kwargs) -> dict:
        # Hello fellow code explorer!
        # Yes, this is the function that single-handedly carries this module
        # Yes, it's a bit jank
        # Yes, you're welcome to tidy it up
        # No, there's no need to change anything
        # It works perfectly fine
        # JUST DON'T *TRY* TO BREAK IT
        # Many thanks, eek
        if "/bots/" in uri:
            rlc = routes["/bots/*"]
            if rlc.ratelimited:
                logger.warning(f"Ratelimted for {rlc.retry_after*1000}ms. Handled under the bucket /bots/*.")
                raise Ratelimited(rlc.retry_after, internal=True)
        if routes["*"].ratelimited:
            logger.warning(
                f"Ratelimited for {routes['*'].retry_after*1000}ms. Handled under the bucket /*."
                f" Perhaps review how many requests you're sending?"
            )
            raise Ratelimited(routes["*"].retry_after, internal=True)

        if kwargs.get("data") and isinstance(kwargs["data"], dict):
            kwargs["data"] = dumps(kwargs["data"])

        expected_codes = kwargs.pop("expected_codes", [200])
        url = _base_ + uri
        await self._wf_s()

        logger.info('Sending "{} {}"...'.format(method, url))
        async with self.session.request(method, url, **kwargs) as response:
            if response.status in range(500, 600):
                raise TopGGServerError()
            else:
                await self.callback("toppy_request", url, method)
                # NOTE: This has moved from just before the return since the hits count as soon as a response
                # is generated (unless it's 5xx).
                if "/bots/" in uri:
                    routes["/bots/*"].add_hit()
                routes["*"].add_hit()

            if "application/json" not in response.headers.get("content-type", "none").lower():
                logger.warning(f"Got unexpected mime type {response.headers['Content-Type']} from top.gg.")
                raise ToppyError("Unexpected response from server.")
            if response.status in [403, 401]:
                raise Forbidden()
            if response.status == 429:
                logging.warning("Unexpected ratelimit. Re-syncing internal ratelimit handler.")
                data = await response.json()
                if "/bots/" in uri:
                    routes["/bots/*"].sync_from_ratelimit(data["retry-after"])
                routes["*"].sync_from_ratelimit(data["retry-after"])

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
        return Bot(**response)

    async def fetch_bots(
        self, limit: int = 50, offset: int = 0, search: dict = None, sort: str = None
    ) -> BotSearchResults:
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
        new_results = []
        for bot in result["results"]:
            bot["state"] = self.bot
            new_results.append(Bot(**bot))
        return BotSearchResults(*new_results, limit=limit, offset=offset)

    async def bulk_fetch_bots(self, limit: int = 500, *args) -> dict:
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
        :return: The results of your search (up to ``limit`` results)
        :rtype: :class:`toppy.models.BotSearchResults`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.Forbidden: You didn't specify a valid API token, or you are banned from the API.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if limit > 30_000:
            raise ValueError("Cannot process more than 30 thousand bots at once (definite ratelimit)")
        results = {}
        remaining = limit
        for i in range(remaining // 500):
            batch = await self.fetch_bots(500, offset=i*500, *args)
            results.update(
                {
                    bot.id: bot
                    for bot in batch.results
                }
            )
            remaining -= 500
        if remaining > 0:
            batch = await self.fetch_bots(remaining, offset=len(results), *args)
            results.update(
                {
                    bot.id: bot
                    for bot in batch.results
                }
            )
        return results

    async def fetch_votes(self) -> List[SimpleUser]:
        r"""
        Fetches the last 1000 voters for your bot.

        :returns: A list of up to 1000 SimpleUser objects who have voted for your bot in the past (any time period).
        :rtype: :class:`py:list`[:class:`toppy.models.SimpleUser`]
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        raw_users = await self._request("GET", f"/bots/{self.bot.user.id}/votes")
        resolved = list(map(lambda u: SimpleUser(**u), raw_users))
        logger.debug(f"Response from fetching votes: {resolved}")
        return resolved

    async def upvote_check(self, user: Union[discord.User, discord.Member, discord.Object]) -> bool:
        r"""
        Checks to see if the provided user has voted for your bot in the pas 12 hours.

        :param user: The user to fetch upvote for.
        :returns: True if the has user voted in the past 12 hours, False if not
        :rtype: :class:`py:bool`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given.
        """
        if not self.bot.is_ready():
            await self.bot.wait_until_ready()
        uri = f"/bots/{self.bot.user.id}/check?userId={user.id}"
        raw_users = await self._request("GET", uri)
        logger.debug(f"Response from fetching upvote check: {raw_users}")
        # Ah yes, three pieces of recycled code. How cool.
        return raw_users["voted"] == 1

    async def get_stats(self, bot: Union[discord.User, discord.Member, discord.Object]) -> BotStats:
        r"""Fetches the server & shard count for a bot.

        NOTE: this does NOT fetch votes. Use the fetch_bot function for that.

        :returns: Basic statistics on the specified bot.
        :rtype: :class:`toppy.models.BotStats`
        :raises toppy.errors.Ratelimited: You've sent too many requests to the API recently.
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given."""
        uri = f"/bots/{bot.id}/stats"
        raw_stats = await self._request("GET", uri)
        logger.debug(f"Response from fetching stats: {raw_stats}")
        return BotStats(**raw_stats)

    async def post_stats(self, force_shard_count: bool = False) -> int:
        r"""
        Posts your bot's current statistics to top.gg

        :type force_shard_count: :class:`py:bool`
        :param force_shard_count: If true, always include shard data, even when it would normally be excluded

        :returns: an integer of how many servers got posted.
        :rtype: :class:`py:int`
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

        response = await self._request("POST", f"/bots/{self.bot.user.id}/stats", data=dumps(stats))
        logger.debug(f"Response from fetching posting stats: {response}")
        await self.callback("guild_post", stats)
        return stats["server_count"]

    async def is_weekend(self) -> bool:
        r"""Returns True or False, depending on if it's a "weekend".

        If it's a weekend, votes count as double.

        :rtype: :class:`py:bool:`
        :raises toppy.errors.ToppyError: Either the server sent an invalid response, or an unexpected response code was given."""
        data = await self._request("GET", f"/weekend")
        return data["is_weekend"]

    async def fetch_user(self, user: Union[discord.User, discord.Member, discord.Object]) -> User:
        """
        Fetches a user's profile from top.gg.

        :param user: Union[discord.User, discord.Member] - Who's top.gg profile to fetch.
        :raises toppy.errors.Forbidden: - Your API token was invalid.
        :raises toppy.errors.NotFound: - The user who you requested does not have a top.gg profile.
        :returns toppy.models.User: The fetched user's profile
        """
        data = await self._request("GET", f"/users/{user.id}")
        return User(**data, state=self.bot)
