.. currentmodule:: toppy

API Reference
=============
This page will describe top.py's client class and it's attributes.

.. note::
    Like discord.py, we use python's in-built logging module. Most things are logged
    via the debug level, and only certain events are logged via warnings.
    You're not missing much if you don't set it up.

Version
~~~~~~~
You can get a version from :attr:`toppy.__version__`

Client
~~~~~~
.. autoclass:: TopGG
    :members:
    :undoc-members:

Client Event Reference
~~~~~~~~~~~~~~~~~~~~~~

_Note: all events must be async._

.. function:: on_guild_post(stats: dict)

    Event dispatched whenever :func:`toppy.client.TopGG.post_stats` is called.

    ``stats`` is a dictionary with the keys ``server_count`` (:class:`int`), ``shards`` (:class:`list`), and
    ``shard_count`` (:class:`int`)

    :param stats: :obj:`py:dict` - Aforementioned stats dictionary

    .. Example: ::

        # Not in a cog
        @bot.event
        async def on_guild_post(stats):
            print("Posted", stats["server_count"], "servers to top.gg")

        # in a cog
        @commands.Cog.listener()
        async def on_guild_post(self, stats):
            print("Posted", stats["server_count"], "servers to top.gg")

.. function:: on_toppy_request(*, url: str, method: Literal["GET", "POST"])

    Event dispatched whenever the internal function :func:`toppy.client.TopGG._request` is used.

    URL is the request URL, and method is the method used on the URL.

    .. warning::
        This function is called on EVERY request, and as such should only really be used to find out why you're
        being ratelimited (if that is happening). The only other use case is to see where your requests are going.

    :param url: :obj:`py:str` - The URL the request was sent to
    :param method: :obj:`py:str` - The method used to request.

    .. Example: ::

        import datetime

        # Not in a cog
        @bot.event
        async def on_toppy_request(*, url, method):
            print(f"[{datetime.datetime.now().strftime('%c')}] {method} {url}")

        # in a cog
        @commands.Cog.listener()
        async def on_toppy_request(self, *, url, method):
            print(f"[{datetime.datetime.now().strftime('%c')}] {method} {url}")

.. function:: on_toppy_stat_autopost(result):

    Event dispatched whenever the internal autopost task succeeds.

    .. note::
        This function takes the exact same argument as :func:`on_guild_post`.
