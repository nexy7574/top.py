import asyncio
import logging
from typing import Coroutine

from aiohttp import web
from .models import cast_vote


__all__ = (
    "create_server",
)


def _create_callback(bot, auth, *, disable_warnings: bool = False, verbose: bool = False):
    async def callback(request: web.Request):
        logging.debug("Got webhook request from {}.".format(request.remote))
        if verbose:
            print(f"Incoming request from {request.remote}")
        if auth:
            user_auth = request.headers.get("Authorization", "")
            if user_auth != auth:
                if not disable_warnings:
                    logging.warning("Got incorrect authorisation from '{}': {}".format(request.remote, user_auth))
                if verbose:
                    print("Got incorrect authorisation from '{}': {}".format(request.remote, user_auth))
                return web.Response(body='{"detail": "unauthorized."}', status=401)
        try:
            data = await request.json()
            if verbose:
                print(f"Data from {request.remote}: {data}")
            vote = cast_vote(data, bot)
        except (TypeError, ValueError, KeyError) as e:
            print(f"Malformed data from {request.remote}: {await request.text()} - {e}")
            return web.Response(body='{"detail": "malformed body."}', status=422)
        if verbose:
            print(f"Dispatched {vote} to on_vote.")
        bot.dispatch("vote", vote)
        return web.Response(body='{"detail": "accepted"}')

    return callback


def start_server(
    bot, *, host: str = "0.0.0.0", port: int = 8080, path: str = "/", auth: str = None, disable_warnings: bool = False,
    verbose: bool = True
) -> Coroutine[None, None, None]:
    """
    Creates a vote webhook server.

    This will listen for webhooks on <host>:<port>[/<path>].

    MAKE SURE YOUR PORT IS FORWARDED AND THAT YOUR AUTH+PATH IS THE SAME AS THAT ON TOP.GG!

    :param bot: Your bot instance
    :param host: The host to run this on. Usually, it's fine to leave this default.
    :param port: The port to listen to. Make sure it's forwarded. This defaults to 8080.
    :param path: The bit after your IP/domain. Defaults to /.
    :param auth: Your authorization you set on your top.gg bot settings. Please don't leave this blank. Please.
    :param disable_warnings: If True, this will disable any sort of warnings that may arise from the web server.
    :param verbose: If True, this will log all requests to stdout.
    :type bot: :class:`discord:discord.Client`
    :type host: :class:`py:str`
    :type port: :class:`py:int`
    :type path: :class:`py:str`
    :type auth: Optional[:class:`py:str`]
    :type disable_warnings: :class:`py:bool`
    :return: A task containing the background wrap for running the server. You're responsible for cleanup.
    :rtype: :class:`py:asyncio.Task`
    """
    async def inner():
        app = web.Application()
        app.add_routes([web.post(path, _create_callback(bot, auth, disable_warnings=disable_warnings))])
        runner = web.AppRunner(app)
        await runner.setup()
        webserver = web.TCPSite(runner, host, port)
        if verbose:
            print(f"Starting top.gg webhook server on {host}:{port}{path}.")
        await webserver.start()

    return inner()


def create_server(*args, **kwargs) -> asyncio.Task:
    """Alias for :function:`start_server`, but imitating the old <1.4.2 behaviour"""
    return args[0].create_task(start_server(*args, **kwargs))
