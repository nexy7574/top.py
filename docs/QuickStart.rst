.. py:currentmodule:: toppy.client

QuickStart
=============
If you're unsure where to start with top.py, there are a few examples on our
github repository `here <https://github.com/EEKIM10/top.py>`_

.. note::
    any examples in this document were written in `py-cord <https://pypi.org/project/py-cord>`_.
    cross-compatibility is not guaranteed.


AutoPosting server count
------------------------
This code will simply automatically post your server count every 30 minutes.

.. code-block:: python3

    import toppy
    import discord
    import os

    bot = discord.Bot()
    bot.toppy = toppy.Client(bot, token=os.environ["TOPPY_TOKEN"], autopost=True)
    # When initialised with 'autopost=True', the bot uses discord.ext.tasks to run a loop
    # every 30 minutes that calls 'Client.post_stats()', and dispatches the result with an event
    # called 'toppy_stat_autopost'. This is the setting that requires least configuration, and
    # is best for most users.

Fetching listed bots
--------------------
In top.py, there are two ways to fetch bots: bulk fetching, and individual fetches.

To bulk fetch, you can use the :func:`TopGG.fetch_bots` function:

.. code-block:: python3

    import toppy
    import discord
    import os
    from discord.ext import pages

    bot = discord.Bot()
    bot.toppy = toppy.Client(bot, token=os.environ["TOPPY_TOKEN"])

    @bot.slash_command(name="query-bots")
    async def query_bots(ctx: discord.ApplicationContext, count: int):
        """Fetches up to <count> bots from top.gg"""
        await ctx.defer()
        _pages = []
        search_results = await bot.toppy.fetch_bots(limit=count)  # fetches up to <count> bots
        for n, _bot in enumerate(search_results.results, start=1):
            owners = " & ".join(f"<@{owner}>" for owner in _bot.owners)
            _pages.append(
                f"({n:,}/{len(results):,}) [{bot.username}#{bot.discriminator} by {owners}](https://top.gg/bot/{bot.id})"
            )
        paginator = pages.Paginator(_pages)
        await paginator.respond(ctx.interaction)

Or you can fetch a specific bot's details, using :func:`TopGG.fetch_bot`, as follows:

.. code-block:: python3

    import toppy
    import discord
    import os

    bot = discord.Bot()
    bot.toppy = toppy.Client(bot, token=os.environ["TOPPY_TOKEN"])

    @bot.user_command(name="Get top.gg details")
    async def query_bot(ctx: discord.ApplicationContext, member: discord.Member):
        await ctx.defer()

        try:
            _bot = await bot.toppy.fetch_bot(member)
        except toppy.errors.NotFound:
            return await ctx.respond(":x: Unknown bot.")
        await interaction.respond(
            f"Username: {_bot.username}\nID: `{_bot.id}`\nLink: https://top.gg/bot/{_bot.id}"
        )

