#
#
#
#
#
#
#
#
#
#
#
#
#
# DO NOT RUN THIS FILE YOURSELF!
# THIS FILE IS FOR DEVELOPMENT PURPOSES
#
# ONLY RUN IT IF YOU NEED TO GET RESPONSES FROM TOP.GG
# FOR THE MOCKUP TEST SERVER.
#
#
#
#
#
#
#
#
#
import asyncio

import requests
import os

key = os.environ["top_token"]


class FakeClientUser:
    id = int(os.getenv("bot_user_id", 619328560141697036))


class _FakeBot:
    loop = asyncio.get_event_loop()
    guilds = []
    shards = []
    user = FakeClientUser()

    def is_ready(self):
        return True

    def dispatch(self, *args, **kwargs):
        pass


bot = _FakeBot()


class Request(dict):
    def __init__(self, endpoint: str, method: str = "GET", data: dict = None):
        super().__init__(endpoint=endpoint, method=method.upper(), data=data)


