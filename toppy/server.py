from aiohttp import web
from .models import Vote


def _create_callback(bot, auth):
    async def callback(request: web.Request):
        if auth:
            if request.headers.get("Authorization", "") != auth:
                return web.Response(body={"detail": "unauthorized."}, status=401)
        bot.dispatch("vote", Vote(await request.json()))
        return web.Response(body={"detail": "accepted"})

    return callback


def create_server(bot, *, host: str = "127.0.0.1", port: int = 8080, path: str = "/", auth: str = None):
    """
    Creates a vote webhook server.
    This will listen for webhooks on <host>:<port>[/<path>].
    MAKE SURE YOUR PORT IS FORWARDED AND THAT YOUR AUTH+PATH IS THE SAME AS THAT ON TOP.GG!

    :param bot: Your bot instance
    :param host: The host to run this on. Usually, it's fine to leave this default.
    :param port: The port to listen to. Make sure it's forwarded. This defaults to 8080.
    :param path: The bit after your IP/domain. Defaults to /.
    :param auth: Your authorization you set on your top.gg bot settings. Please don't leave this blank. Please.
    :return: An asyncio.Task containing the background wrap for running the server. You're responsible for cleanup.
    """
    app = web.Application()
    app.add_routes([web.post(path, _create_callback(bot, auth))])
    return bot.loop.create_task(bot.loop.run_in_executor(web.run_app, app, host=host, port=port))
