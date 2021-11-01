import logging
from aiohttp import web
from .models import Vote


def _create_callback(bot, auth, *, disable_warnings: bool = False):
    async def callback(request: web.Request):
        logging.debug("Got webhook request from {}.".format(request.remote))
        if auth:
            user_auth = request.headers.get("Authorization", "")
            if user_auth != auth:
                if not disable_warnings:
                    logging.warning("Got incorrect authorisation from '{}': {}".format(request.remote, user_auth))
                return web.Response(body='{"detail": "unauthorized."}', status=401)
        try:
            vote = Vote(await request.json())
        except TypeError:
            return web.Response(body='{"detail": "malformed body."}', status=422)
        bot.dispatch("vote", vote)
        return web.Response(body='{"detail": "accepted"}')

    return callback


async def _init_server(
    bot, *, host: str = "0.0.0.0", port: int = 8080, path: str = "/", auth: str = None, disable_warnings: bool = False
):
    app = web.Application()
    app.add_routes([web.post(path, _create_callback(bot, auth, disable_warnings=disable_warnings))])
    runner = web.AppRunner(app)
    await runner.setup()
    webserver = web.TCPSite(runner, host, port)
    return await webserver.start()


def create_server(
    bot, *, host: str = "0.0.0.0", port: int = 8080, path: str = "/", auth: str = None, disable_warnings: bool = False
):
    """
    Creates a vote webhook server.

    This will listen for webhooks on <host>:<port>[/<path>].

    MAKE SURE YOUR PORT IS FORWARDED AND THAT YOUR AUTH+PATH IS THE SAME AS THAT ON TOP.GG!

    Example:
        .. code-block::

            from toppy.server import create_server
            bot.vote_server = create_server(


    :param bot: Your bot instance
    :param host: The host to run this on. Usually, it's fine to leave this default.
    :param port: The port to listen to. Make sure it's forwarded. This defaults to 8080.
    :param path: The bit after your IP/domain. Defaults to /.
    :param auth: Your authorization you set on your top.gg bot settings.
    :param disable_warnings: If True, this will disable any sort of warnings that may arise from the web server.
    :type bot: :class:`discord:discord.Client`
    :type host: :class:`py:str`
    :type port: :class:`py:int`
    :type path: :class:`py:str`
    :type auth: Optional[:class:`py:str`]
    :type disable_warnings: :class:`py:bool`
    :return: A task containing the background wrap for running the server. You're responsible for cleanup.
    :rtype: :class:`py:asyncio.Task`
    """
    if not bool(auth):
        raise ValueError("An authentication token must be provided to the top.py server (as of 1.4.0a1).")

    if not all(x.isdigit() for x in host.split(".")):
        raise TypeError("%r does not appear to be a valid IP." % host)

    if not path.startswith("/"):
        raise ValueError("%r should start with a leading slash (for example: /vote)")

    return bot.loop.create_task(
        _init_server(
            bot,
            host=host,
            port=port,
            path=path,
            auth=auth,
            disable_warnings=disable_warnings
        )
    )
