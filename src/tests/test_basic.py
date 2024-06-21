import logging
import json
import time
from pathlib import Path

import discord
from aioresponses import aioresponses

import pytest

logging.basicConfig(level=logging.DEBUG)

SAMPLES = Path(__file__).parent / "samples"


@staticmethod
def _load_response(name: str, model: type = None):
    with open(SAMPLES / name, "r") as f:
        x = json.loads(f.read())
    if model:
        return model(**x)
    return x


def _get_topgg_client():
    from toppy.client import TopGG
    from discord import Client, Intents
    client = Client(intents=Intents.default())
    topgg = TopGG(client, token="...")
    return topgg


@pytest.mark.parametrize(
    "path",
    [
        "/bots/*",
        "*"
    ]
)
def test_ratelimiter(path: str):
    from toppy.ratelimiter import Ratelimit

    route = Ratelimit("/test", 100, 1, 1)

    assert route.hits == 0
    assert not route.ratelimited
    assert route.retry_after == 0.0

    # test hits
    _max = route.max_hits
    for i in range(_max):
        route.add_hit()
        if route.hits >= route.max_hits:
            assert route.ratelimited, f"not ratelimited after {i+1}/{route.max_hits} hits, {route!r}"
            assert route.retry_after != 0.0, f"not ratelimited after {i+1}/{route.max_hits} hits, {route!r}"
        else:
            assert not route.ratelimited, f"ratelimited after {i+1}/{route.max_hits} hits, {route!r}"


@pytest.mark.asyncio()
async def test_search_bots():
    from toppy.models.bot import BotSearchResult

    with aioresponses() as m:
        m.get(
            "https://top.gg/api/bots",
            payload=_load_response("get_bots.json")
        )
        topgg = _get_topgg_client()
        result = await topgg.fetch_bots(10, 0, None, None)
        assert isinstance(result, BotSearchResult), "Result is not BotSearchResult"
        assert len(result.results) == 10, "Results not 10, is %d" % len(result.results)
        assert result.limit == 10, "Limit not 50"
        assert result.offset == 0, "Offset not 0"
        assert result.count == 10, "Count not 50"
        assert result.total == 42969, "Total not 42969"


@pytest.mark.asyncio()
async def test_search_bot():
    from toppy.models.bot import Bot

    with aioresponses() as m:
        m.get(
            "https://top.gg/api/bots/235148962103951360",
            payload=_load_response("get_bot.json")
        )
        topgg = _get_topgg_client()
        result = await topgg.fetch_bot(discord.Object(id=235148962103951360))
        assert isinstance(result, Bot), "Result is not Bot"


def test_short_ratelimit():
    from toppy.ratelimiter.bucket import Ratelimit

    route = Ratelimit(
        route="/",
        max_hits=2,
        cooldown=1,
        per=1
    )
    for i in range(10):
        route.add_hit()
        if route.ratelimited:
            break
        elif i > 2 and not route.ratelimited:
            raise AssertionError("max hits exceeded and not ratelimited")
    assert route.retry_after <= 1.1, f"retry_after > 1.1 {route!r}"
    time.sleep(0.1)
    assert route.hits != 0, f"No hits {route!r}"
    assert route.ratelimited, f"Not ratelimited {route!r}"
    assert route.retry_after, f"No retry_after {route!r}"
    time.sleep(route.retry_after + 0.1)
    assert not route.retry_after, f"retry_after not reset {route!r}"
    assert not route.ratelimited, f"ratelimited after cooldown period {route!r}"
    route.add_hit()
    assert not route.ratelimited, f"Still ratelimited after cooldown period {route!r}"
