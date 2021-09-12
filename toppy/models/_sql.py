import datetime
from typing import Literal

from aiosqlite import Connection


class Vote:
    """Represents a vote entry.

    .. note::
        This class is entirely read only, and should not be created in the user-end.
    """

    def __init__(self, vote_id: int, user_id: int, vote_worth: Literal[1, 2], voted_at: float):
        self.__data = (
            vote_id,
            user_id,
            vote_worth,
            datetime.datetime.utcfromtimestamp(voted_at)
        )

    @property
    def vote_id(self) -> int:
        """
        The internal ID of this vote. Only used for the database.

        :returns: An incremental integer
        :rtype: :class:`py:int`
        """
        return self.__data[0]

    @property
    def user_id(self) -> int:
        """
        Represents the ID of the user that voted.

        :returns: User ID
        :rtype: :class:`py:int`
        """
        return self.__data[1]

    @property
    def vote_worth(self) -> Literal[1, 2]:
        """
        How many votes this vote was worth.

        This is always 1, unless the vote was made on the weekend (:meth:`toppy.TopGG.is_weekend`), in which case
        it will be 2.

        :returns: How many votes this vote was worth, Literal[1, 2]
        :rtype: :class:`py:int`
        """
        return self.__data[2]

    @property
    def timestamp(self) -> datetime.datetime:
        """
        A (naive) :class:`py:datetime.datetime` for when this vote was cast.

        :returns: naive datetime
        :rtype: :class:`py:datetime.datetime`
        """
        return self.__data[3]


class SQLManager:

    def __init__(self, connection: Connection):
        self.connection = connection

    async def get_vote(self, vote_id: int):
        pass
