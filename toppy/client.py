import aiohttp
import asyncio
from typing import Union
# noinspection PyPep8Naming
from discord import Client as C, AutoShardedClient as AC
# noinspection PyPep8Naming
from discord.ext.commands import Bot as B, AutoShardedBot as AB


class TopGG:
    """
    The client class for the top.gg API.

    This class handles everything for the top.gg API, APART FROM voting webhooks - Those are handled by the server
    class.
    """

    def __init__(
            self,
            bot: Union[C, B, AC, AB],
            *,
            token: str
    ):
        self.bot = bot
        self.token = token
