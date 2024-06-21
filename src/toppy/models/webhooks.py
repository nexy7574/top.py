from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, AnyStr, Literal, Optional, Union


__all__ = (
    "BotVoteWebhookPayload",
    "ServerVoteWebhookPayload"
)


@dataclass
class BotVoteWebhookPayload:
    """
    Represents the payload received as part of a bot vote webhook

    See Also: https://docs.top.gg/docs/Resources/webhooks#bot-webhooks
    """
    bot: str
    """Discord ID of the bot that received a vote."""

    user: str
    """Discord ID of the user who voted."""

    type: Literal["upvote", "test"]
    """The type of the vote (should always be "upvote" except when using the test button it's "test")."""

    isWeekend: bool
    """Whether the weekend multiplier is in effect, meaning users votes count as two."""

    query: Optional[str] = None
    """Query string params found on the /bot/:ID/vote page. Example: ?a=1&b=2."""


@dataclass
class ServerVoteWebhookPayload:
    """
    Represents the payload received as part of a server vote webhook

    See Also: https://docs.top.gg/docs/Resources/webhooks#server-webhooks
    """
    guild: str
    """Discord ID of the guild that received a vote."""

    user: str
    """Discord ID of the user who voted."""

    type: Literal["upvote", "test"]
    """The type of the vote (should always be "upvote" except when using the test button it's "test")."""

    query: Optional[str] = None
    """Query string params found on the /bot/:ID/vote page. Example: ?a=1&b=2."""
