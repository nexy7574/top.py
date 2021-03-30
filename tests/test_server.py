import asyncio

from toppy.server import _create_callback, Vote


POST_DATA = {
  "bot": "619328560141697036",
  "user": "421698654189912064",
  "type": "test",
  "isWeekend": False,
  "query": "?test=data&notRandomNumber=8"
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

    async def json(self):
        return POST_DATA


def test_vote_server():
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobar")
    loop.run_until_complete(cb(FakeRequest()))


def test_vote_server_broken_creds():
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobarbazz")
    loop.run_until_complete(cb(FakeRequest()))


def test_vote_server_broken_data():
    # This is unlikely to happen in a real webhook, but we'll test that it's handled anyway
    sponge = Sponge()
    loop = asyncio.get_event_loop()

    cb = _create_callback(sponge, "foobarbazz")
    loop.run_until_complete(cb(FakeRequest()))
