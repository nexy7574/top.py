try:
    from pydantic.dataclasses import dataclass
    from pydantic import Field as field
except ImportError:
    from dataclasses import dataclass, field

from typing import List, Literal, Optional, Union

__all__ = (
    "Bot",
    "BotSearchResult",
    "VoteResult",
    "Last1000VotesResponse",
    "BotStatsResult",
    "IndividualUserVoteResult",
    "BotStatsPayload"
)


@dataclass
class Bot:
    """
    Represents a bot.
    This is used by the likes of search and find_one

    See Also: https://docs.top.gg/docs/API/bot#bot-structure
    """
    id: str
    """The id of the bot"""

    username: str
    """The username of the bot"""

    discriminator: str
    """The discriminator of the bot"""

    lib: str
    """The library of the bot"""

    prefix: str
    """The prefix of the bot"""

    shortdesc: str
    """The short description of the bot"""

    tags: List[str]
    """The tags of the bot"""

    owners: List[str]
    """Snowflakes of the owners of the bot. First one in the array is the main owner"""

    date: str
    """The date when the bot was approved"""

    certifiedBot: bool
    """The certified status of the bot"""

    points: int
    """The amount of upvotes the bot has"""

    monthlyPoints: int
    """The amount of upvotes the bot has this month"""

    donatebotguildid: Optional[str] = None
    """The guild id for the donatebot setup"""

    vanity: Optional[str] = None
    """The vanity url of the bot"""

    server_count: Optional[int] = None
    """The amount of servers the bot has according to posted stats."""

    shard_count: Optional[int] = None
    """The amount of shards the bot has according to posted stats."""

    invite: Optional[str] = None
    """The custom bot invite url of the bot"""

    website: Optional[str] = None
    """The website url of the bot"""

    support: Optional[str] = None
    """The support server invite code of the bot"""

    github: Optional[str] = None
    """The link to the github repo of the bot"""

    longdesc: Optional[str] = None
    """The long description of the bot. Can contain HTML and/or Markdown"""

    avatar: Optional[str] = None
    """The avatar hash of the bot's avatar"""

    defAvatar: Optional[str] = None
    """The cdn hash of the bot's avatar if the bot has none"""


@dataclass
class BotSearchResult:
    """
    Represents a bot search result.

    See Also: https://docs.top.gg/docs/API/bot#search-bots
    """

    results: List[Bot]
    """The matching bots"""

    limit: int
    """The limit used"""

    offset: int
    """The offset used"""

    count: int
    """The length of the results array"""

    total: int
    """The total number of bots matching your search"""


@dataclass
class VoteResult:
    """
    Represents a vote from the most recent 1000 votes.

    See Also: https://docs.top.gg/docs/API/bot#last-1000-votes
    """
    username: str
    id: str
    avatar: str


Last1000VotesResponse = List[VoteResult]


@dataclass
class BotStatsResult:
    """
    Represents the response of fetching a bot's statistics

    See Also: https://docs.top.gg/docs/API/bot#bot-stats
    """
    shards: List[int] = field(default_factory=list)
    """The amount of servers the bot is in per shard."""

    server_count: Optional[int] = None
    """The amount of servers the bot is in"""

    shard_count: Optional[int] = None
    """The amount of shards a bot has"""


@dataclass
class IndividualUserVoteResult:
    """
    Represents a user's vote for a bot

    See Also: https://docs.top.gg/docs/API/bot#individual-user-vote
    """
    voted: Literal[0, 1]
    # This is only here for completion


@dataclass
class BotStatsPayload:
    """
    Represents the payload sent to top.gg when posting bot stats

    See Also: https://docs.top.gg/docs/API/bot#post-body
    """
    server_count: Union[int, List[int]]
    """Amount of servers the bot is in. If an Array, it acts like shards"""

    shards: Optional[List[int]] = None
    """Amount of servers the bot is in per shard."""

    shard_id: Optional[int] = None
    """The zero-indexed id of the shard posting. Makes server_count set the shard specific server count."""

    shard_count: Optional[int] = None
    """The amount of shards the bot has"""
