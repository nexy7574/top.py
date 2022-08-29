from typing import Union, TYPE_CHECKING, Optional, AnyStr, Any
from enum import Enum

import discord

from .user import _ReprMixin


__all__ = (
    "VoteType",
    "SharedVote",
    "ServerVote",
    "BotVote",
    "cast_vote"
)


class VoteType(Enum):
    UPVOTE = "upvote"
    """Represents a regular vote"""

    TEST = "test"
    """Represents a test vote"""


class SharedVote:
    """
    Attributes:
        type: :class:`VoteType`
        query: :class:`py:str`
    """

    if TYPE_CHECKING:
        _state: Any
        _user: str
        type: VoteType
        """The type of vote"""

        query: Optional[AnyStr]
        """The query in vote string"""

    def __init__(self, state, user, _type, query):
        self._state = state
        self._user = user
        self.type = VoteType(_type)
        self.query = query

    @property
    def user(self) -> Union[discord.User, discord.Object]:
        """
        Returns the user who voted.

        .. warning::
            If you don't have the member cache, or members intent, then this function will always return
            :obj:`discord:discord.Object`, as that is the default when the get_user call fails.

        :returns: :class:`discord:discord.User` or :class:`discord:discord.Object`.
        """
        us = None
        if self._state:
            us = self._state.get_user(int(self._user))
        return us or discord.Object(int(self._user))


class ServerVote(SharedVote, _ReprMixin):
    """
    Represents a vote for a server listing

    Attributes:
        type: :class:`VoteType`

        query: :class:`py:str`
    """
    def __init__(self, data: dict, *, state=None):
        super().__init__(
            state,
            data["user"],
            data["type"],
            data.get("query", "")
        )
        self._guild = data["guild"]

    @property
    def guild(self) -> Union[discord.Guild, discord.Object]:
        """
        Returns the guild that was voted on.

        .. warning::
            similar to :attr:`SharedVote.user`, this function will return :obj:`discord:discord.Object` if the
            internal cache lookup returns nothing.

        :returns: :class:`discord:discord.Guild` or :class:`discord:discord.Object`.
        """
        us = discord.Object(int(self._guild))
        if self._state:
            us = self._state.get_guild(us.id) or us
        return us

    @property
    def user(self):
        return super().user


class BotVote(SharedVote, _ReprMixin):
    """
    Represents a vote for a Bot listing

    Attributes:
        type: :class:`VoteType`
            The type of vote (test or upvote)

        is_weekend: :class:`py:bool`
            Represents if votes are worth double

        isWeekend: :class:`py:bool`
            alias for :attr:`BotVote.is_weekend`

        query: :class:`py:str`
            The querystring while voting
    """

    def __init__(self, data: dict, *, state=None):
        super().__init__(
            state,
            data["user"],
            data["type"],
            data.get("query", "")
        )
        self._bot = data["bot"]
        self.is_weekend: bool = data.get("isWeekend", False)
        self.isWeekend = self.is_weekend  # alias

    @property
    def bot(self) -> Union[discord.User, discord.Object]:
        """
        The resolved bot user for this vote. This is, hopefully, always your current bot.

        .. warning::
            If the internal lookup fails, this returns a :obj:`discord:discord.Object` by default.

        :returns: :class:`discord:discord.User` or :class:`discord:discord.Object`.
        """
        us = None
        if self._state:
            us = self._state.get_user(int(self._bot))
        return us or discord.Object(int(self._bot))

    @property
    def user(self):
        return super().user


def cast_vote(data: dict, state=None) -> Union[BotVote, ServerVote]:
    if data.get("bot") is not None:
        v = BotVote
    else:
        v = ServerVote
    return v(data, state=state)
