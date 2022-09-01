import datetime
import time

import pytest


def test_import_client():
    from toppy.client import TopGG


def test_import_server():
    from toppy.server import create_server, _create_callback


def test_init_client():
    from toppy.client import TopGG

    TopGG(None, token="hi", autopost=False)


@pytest.mark.parametrize(
    "path",
    [
        "/bots/*",
        "*"
    ]
)
def test_ratelimiter(path: str):
    from toppy.ratelimiter import routes

    route = routes[path]

    assert route.hits == 0
    assert route.expires == datetime.datetime.min
    assert not route.ratelimited
    assert route.retry_after == 0.0

    # test hits
    _max = route.max_hits
    for i in range(_max):
        route.add_hit()
        if route.hits >= route.max_hits:
            assert route.ratelimited, f"not ratelimited after {i+1}/{route.max_hits} hits"
            assert route.retry_after != 0.0, f"not ratelimited after {i+1}/{route.max_hits} hits"
        else:
            assert not route.ratelimited, f"ratelimited after {i+1}/{route.max_hits} hits"


def test_short_ratelimit():
    from toppy.ratelimiter.bucket import Ratelimit

    route = Ratelimit(
        route="/",
        hits=2,
        cooldown=1
    )
    for i in range(10):
        route.add_hit()
        if route.ratelimited:
            break
        elif i > 2 and not route.ratelimited:
            raise AssertionError("max hits exceeded and not ratelimited")
    assert route.retry_after <= 1.1
    time.sleep(0.1)
    assert route.hits != 0
    assert route.ratelimited
    assert route.retry_after
    time.sleep(route.retry_after + 0.1)
    assert not route.retry_after
    assert not route.ratelimited
    route.add_hit()
    assert not route.ratelimited, "Still ratelimited after cooldown period"
