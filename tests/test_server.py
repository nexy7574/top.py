import asyncio
import json
from typing import Union

import discord
from aiohttp.web import Response
import pytest

from toppy.server import _create_callback, cast_vote
from toppy.models import VoteType, BotVote, ServerVote

Vote = Union[BotVote, ServerVote]

pytest_plugins = ("pytest_asyncio",)


POST_DATA = {
    "bot": "619328560141697036",
    "user": "421698654189912064",
    "type": "test",
    "isWeekend": False,
    "query": "?test=data&notRandomNumber=8",
}


class Sponge:
    def dispatch(self, _, vp: Vote):
        assert vp.bot.id == int(POST_DATA["bot"])
        assert vp.user.id == int(POST_DATA["user"])
        assert vp.type == VoteType.TEST
        assert vp.is_weekend is False
        assert vp.query == POST_DATA["query"]

    def get_user(self, _id):
        return discord.Object(_id)


class FakeRequest:
    headers = {"Authorization": "foobar"}
    remote = "127.0.0.1"

    def __init__(self, new_data=None):
        if new_data is None:
            new_data = POST_DATA
        self.data = new_data

    async def json(self):
        return self.data

    async def text(self):
        return json.dumps(self.data)


@pytest.mark.asyncio
async def test_vote_server():
    sponge = Sponge()
    cb = _create_callback(sponge, "foobar")
    response = await cb(FakeRequest())
    assert response.status == 200


@pytest.mark.asyncio
async def test_vote_server_broken_creds():
    sponge = Sponge()
    cb = _create_callback(sponge, "foobarbazz")
    response: Response = await cb(FakeRequest())
    assert response.status == 401


@pytest.mark.asyncio
async def test_vote_server_broken_data():
    # This is unlikely to happen in a real webhook, but we'll test that it's handled anyway
    sponge = Sponge()
    cb = _create_callback(sponge, "foobar")
    _data = POST_DATA.copy()
    for key in _data.keys():
        # noinspection PyTypeChecker
        _data[key] = None
    response: Response = await cb(FakeRequest(_data))
    assert response.status == 422


@pytest.mark.parametrize(
    ("data", "expected_type"),
    (
            (
                {
                    "guild": "729779146682793984",
                    "user": "421698654189912064",
                    "type": "test",
                    "query": ""
                },
                ServerVote
            ),
            (
                {
                    "bot": "729335748670783488",
                    "user": "421698654189912064",
                    "type": "test",
                    "isWeekend": False,
                    "query": ""
                },
                BotVote
            )
    )
)
def test_vote_cast(data: dict, expected_type: type):
    casted = cast_vote(data)
    assert isinstance(casted, expected_type)
