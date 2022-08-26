.. currentmodule:: toppy

Vote Server Reference
=====================


Creating the webhook server
---------------------------

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


The create server function
--------------------------
.. autofunction:: create_server


Vote types
----------
The following vote types may be passed to the event :obj:`on_vote`:

.. class:: VoteType

    .. py:attribute:: TEST

    .. py:attribute:: UPVOTE


.. autoclass:: ServerVote
    :members:
    :undoc-members:
    :private-members:


.. autoclass:: BotVote
    :members:
    :undoc-members:
    :private-members:


Vote Event Reference
--------------------

.. function:: on_vote(vote: Union[BotVote, ServerVote]):

    Dispatched whenever there is a vote. Be sure to check the vote type and class.
