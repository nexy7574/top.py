from datetime import datetime
from typing import Literal, Optional, List, Union, Iterable

import discord
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
            datetime.utcfromtimestamp(voted_at)
        )

    @property
    def vote_id(self) -> Optional[int]:
        """
        The internal ID of this vote. Only used for the database.

        .. warning::
            This is ``None`` ONLY if returned by :meth:`SQLManager.create_vote`.

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
    def timestamp(self) -> datetime:
        """
        A (naive) :class:`py:datetime.datetime` for when this vote was cast.

        :returns: naive datetime
        :rtype: :class:`py:datetime.datetime`
        """
        return self.__data[3]


class SQLManager:

    def __init__(self, connection: Connection):
        self.connection = connection

    async def __init(self):
        statements = (
            """
            CREATE TABLE IF NOT EXISTS votes (
                vote_id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                vote_worth INTEGER CHECK(vote_worth>0 AND vote_worth<2),
                timestamp REAL NOT NULL
            );
            """,
        )
        for statement in statements:
            await self.connection.execute(statement)
        await self.connection.commit()

    async def execute(self, *args, **kwargs):
        await self.__init()
        return await self.connection.execute(*args, **kwargs)

    async def get_vote(self, vote_id: int) -> Optional[Vote]:
        async with self.execute(
            """
            SELECT vote_id, user_id, vote_worth, timestamp
            FROM votes
            WHERE vote_id=?;
            """,
                (vote_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return
            return Vote(*row)

    async def get_votes(self, *, before: datetime = None, after: datetime = None):
        votes = []
        for vote in await self.get_all_votes():  # needless computation but who cares :)
            if before is not None:
                if vote.timestamp > before:
                    continue
            if after is not None:
                if vote.timestamp < after:
                    continue
            votes.append(vote)
        return votes

    async def get_all_votes(self, *, limit: int = None) -> List[Vote]:
        votes = []
        async with self.execute(
            """
            SELECT vote_id, user_id, vote_worth, timestamp
            FROM votes;
            """
        ) as cursor:
            async for row in cursor:
                if limit is not None and len(votes) >= limit:
                    break
                votes.append(Vote(*row))
        return votes

    async def get_votes_by(self, user: Union[discord.User, discord.Member]) -> Iterable[Vote]:
        async with self.execute(
            """
            SELECT vote_id, user_id, vote_worth, timestamp
            FROM votes
            WHERE user_id=?;
            """,
                (user.id,)
        ) as cursor:
            return map(lambda v: Vote(*v), await cursor.fetchall())

    async def create_vote(self, user: Union[discord.User, discord.Member], vote_worth: Literal[1, 2]) -> Vote:
        now = datetime.utcnow()
        await self.execute(
            """
            INSERT INTO votes (vote_id, user_id, vote_worth, timestamp)
            VALUES (null, ?, ?, ?);
            """,
            (
                user.id,
                vote_worth,
                now.timestamp()
            )
        )
        await self.connection.commit()
        # noinspection PyTypeChecker
        return Vote(None, user.id, vote_worth, now.timestamp())
