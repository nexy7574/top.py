from typing import Union

import discord

from .user import _ReprMixin


class Vote(_ReprMixin):
    def __init__(self, data: dict, *, state=None):
        self._bot = int(data["bot"])
        self._user = int(data["user"])

        self._type: str = data["type"]

        self.is_test: bool = self._type == "test"

        self.is_weekend: bool = data["isWeekend"]
        self.isWeekend = self.is_weekend  # alias

        self.query = data["query"]

        self._state = state

    @property
    def bot(self) -> Union[discord.User, discord.Object]:
        """
        The resolved bot user for this vote. This is, hopefully, always your current bot.

        :return: discord.User (if resolvable) or a discord.Object
        """
        us = None
        if self._state:
            us = self._state.get_user(self._bot)
        return us or discord.Object(self._bot)

    @property
    def user(self) -> Union[discord.User, discord.Object]:
        """
        The same as Vote.bot, except for the user who voted instead.
        """
        us = None
        if self._state:
            us = self._state.get_user(self._user)
        return us or discord.Object(self._user)
