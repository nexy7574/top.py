def test_import_client():
    from toppy.client import TopGG


def test_import_server():
    from toppy.server import create_server, _create_callback


def test_init_client():
    from toppy.client import TopGG
    TopGG(
        None,
        token="hi",
        autopost=False
    )
