import logging
from asyncio import Task

try:
    from fastapi import FastAPI, Header, Request
    from fastapi.responses import JSONResponse
except ImportError:
    logging.warning("fastapi is not installed. The webhook server will be unsupported.")
    JSONResponse = None
    Header = None
    FastAPI = None
    Request = None

try:
    from uvicorn import Server, Config
except ImportError:
    logging.warning("uvicorn is not installed. The webhook server will be unsupported.")
    Server = None
    Config = None

try:
    from pydantic import BaseModel

    class VotePayload(BaseModel):
        bot: str
        user: str
        type: str
        isWeekend: bool
        query: str = None


except ImportError:
    logging.warning("pydantic is not installed. The webhook server will be unsupported.")
    VotePayload = None


class WebhookServer:
    def __init__(self, bot, path: str = "/vote", port: int = 8080, auth: str = None, *, app: FastAPI):
        self.path = path
        self.port = port
        self.auth = auth
        self.app = app

        self.bot = bot

        self.app.add_route(path, self.on_vote_request, ["POST"])

    async def on_vote_request(self, req: Request, body: VotePayload, Authorization: str = Header(...)):
        if self.auth and self.auth != Authorization:
            logging.debug(f"Rejecting incoming vote request from {req.client.host} ({body}) due to incorrect auth.")
            return JSONResponse({"message": "Incorrect authorization."}, 401)

        if not self.bot.is_ready():
            await self.bot.wait_until_ready()

        if body.type == "test":
            self.bot.dispatch("dbl_test", body)
        else:
            data = {
                "bot": self.bot.user,
                "user": self.bot.get_user(int(body.user)) or int(body.user),
                "type": "vote",
                "is_weekend": body.isWeekend,
                "query": body.query,
            }
            self.bot.dispatch("dbl_vote", data)
            self.bot.dispatch("dbl_vote_raw", body)
        return JSONResponse({"message": "Accepted."}, 202)


def start_webhook_server(bot, host: str = "127.0.0.1", path="/vote", port=8080, auth: str = None) -> Task:
    """
    Starts the webhook server.

    :param bot: your bot or client
    :param host: The host to listen to. Defaults to 127.0.0.1
    :param path: the path votes are POSTed to. e.g. /vote -> http://localhost:8080/vote
    :param port: the port to listen to. Defaults to 8080
    :param auth: the auth to listen for. Make sure this matches the one in your top.gg page.
    :return: an asyncio task. You are responsible for cancelling the task on shutdown.
    """
    if not all((FastAPI, Server, VotePayload)):
        raise TypeError("You have not installed the required packages to use the webhook server.")
    app = FastAPI(include_in_schema=False)
    server_instance = WebhookServer(bot, path, port, auth, app=app)
    config = Config(
        server_instance.app,
        host=host,
        port=port,
        lifespan="on",
        access_log=False,
        use_colors=False,
        forwarded_allow_ips=["*"],
    )
    config.setup_event_loop()
    server = Server(config)
    return bot.loop.create_task(server.serve(), name="Top.py webhook server")
