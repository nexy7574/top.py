import asyncio
from aiohttp.web import Response
import pytest

from toppy.server import _create_callback, Vote


POST_DATA = {
    "bot": "619328560141697036",
    "user": "421698654189912064",
    "type": "test",
    "isWeekend": False,
    "query": "?test=data&notRandomNumber=0",
}


class Sponge:
    def dispatch(self, _, vp: Vote):
        assert vp.bot.id == int(POST_DATA["bot"])
        assert vp.user.id == int(POST_DATA["user"])
        assert vp.is_test is True
        assert vp.is_weekend is False
        assert vp.query == POST_DATA["query"]


class FakeRequest:
    headers = {"Authorization": "foobar"}
    remote = "127.0.0.1"

    def __init__(self, new_data=POST_DATA):
        self.data = new_data

    async def json(self):
        return self.data


def test_vote_server():
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobar")
    response = loop.run_until_complete(cb(FakeRequest()))
    assert response.status == 200


def test_vote_server_broken_creds():
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobarbazz")
    response: Response = loop.run_until_complete(cb(FakeRequest()))
    assert response.status == 401


def test_vote_server_broken_data():
    # This is unlikely to happen in a real webhook, but we'll test that it's handled anyway
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobar")
    _data = POST_DATA.copy()
    for key in _data.keys():
        _data[key] = None
    response: Response = loop.run_until_complete(cb(FakeRequest(_data)))
    assert response.status == 422
