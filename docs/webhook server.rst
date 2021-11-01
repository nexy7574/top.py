.. currentmodule:: toppy.server

Vote Server Reference
=====================


Creating the webhook server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block::

    from discord.ext import commands
    from toppy import server
    bot = commands.Bot("!")
    bot.webhook_server = bot.loop.run_until_complete(server.create_server(
        bot,
        "0.0.0.0",
        8080,
        "/vote",
        "super cool auth secret"
    ))
    bot.run("...")
    bot.webhook_server.cancel()  # closes the server. Not really needed when the program is quitting, but oh well.

.. function:: create_server(bot, *, host: str = "0.0.0.0", port: int = 8080, path: str = "/", auth: str = None, disable_warnings: bool = False)

    Creates a vote webhook server.

    This will listen for webhooks on <host>:<port>[/<path>] (default: http://127.0.0.1:8080/).

    .. danger::
        Please ensure that your port (default being 8080) is port-forwarded. Otherwise, your server will be unable to
        receive requests from top.gg.

        Furthermore, please make sure your auth is set AND matches that on top.gg.

    :param bot: Your bot instance
    :param host: The host to run this on. Usually, it's fine to leave this default.
    :param port: The port to listen to. Make sure it's forwarded. This defaults to 8080.
    :param path: The bit after your IP/domain. Defaults to /.
    :param auth: Your authorization you set on your top.gg bot settings. Please don't leave this blank. Please.
    :param disable_warnings: If True, this will disable any sort of warnings that may arise from the web server.
    :type bot: :class:`discord:discord.Client`
    :type host: :class:`py:str`
    :type port: :class:`py:int`
    :type path: :class:`py:str`
    :type auth: Optional[:class:`py:str`]
    :type disable_warnings: :class:`py:bool`
    :return: A task containing the background wrap for running the server. You're responsible for cleanup.
    :rtype: :class:`py:asyncio.Task`