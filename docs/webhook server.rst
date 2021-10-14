.. currentmodule:: toppy.server

Vote Server Reference
=====================


Creating the webhook server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example:

.. code-block::

    from discord.ext import commands
    from toppy import server
    bot = commands.Bot("!")
    bot.webhook_server = bot.loop.run_until_complete(server.create_server(
        bot,
        "0.0.0.0",
        8080,
        "/vote",
        "super cool auth secret"
    ))
    bot.run("...")
    bot.webhook_server.cancel()  # closes the server. Not really needed when the program is quitting, but oh well.

.. autofunc:: create_server