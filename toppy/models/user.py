from datetime import datetime
from textwrap import shorten
from typing import Optional, List

from discord import User as DiscordUser
from discord.colour import Colour
from discord.utils import oauth_url as invite


class WeakAttr(dict):
    """A simple class that takes a dictionary and allows fetching of items through attributes."""

    def __getattr__(self, item):
        result = self.get(item)
        if result:
            return result
        raise AttributeError("WeakAttr has no attribute '%s'" % item)


class _ReprMixin(object):
    def __repr__(self):
        x = self.__class__.__name__ + "("
        args = []
        for attr_name, attr_value in self.__dict__.items():
            if isinstance(attr_value, str):
                value = attr_value.replace('"', r"\"")
                args.append(f'{attr_name}="{value}"')
            elif isinstance(attr_value, (tuple, list, set)):
                args.append(f"{attr_name}=" + '"' + ", ".join(map(str, attr_value)) + '"')
            else:
                args.append(f"{attr_name}={repr(attr_value)}")
        args = ", ".join((shorten(x, 100) for x in args))
        x += args + ")"
        return x


class UserABC(_ReprMixin):
    id: int
    username: str
    discriminator: str
    user_avatar: str
    default_avatar: str
    avatar: str


class SimpleUser(_ReprMixin):
    """A model representing the "simple user" object returned by /bots/{id}/votes."""

    def __init__(self, **kwargs):
        self.id = int(kwargs.pop("id"))
        self.discriminator = kwargs.pop("discriminator", "#0000")
        self.username = kwargs.pop("username")
        self.avatar = kwargs.pop("avatar", None)


class User(UserABC, _ReprMixin):
    """
    Model representing a top.gg user's account.

    This class conforms to the discord.User ABC.
    """

    def __init__(self, **kwargs):
        self.id: int = int(kwargs.pop("id"))
        self.username: str = kwargs.pop("username")
        self.discriminator: str = kwargs.pop("discriminator")
        self.user_avatar: Optional[str] = kwargs.pop("avatar", None)
        self.default_avatar: str = kwargs.pop("defAvatar")
        self.avatar: str = self.user_avatar or self.default_avatar
        self.bio: Optional[str] = kwargs.pop("bio", None)
        self.banner_url: Optional[str] = kwargs.pop("banner", None)
        self.socials: WeakAttr = WeakAttr(kwargs.pop("social"))
        self._raw_colour = (kwargs.get("color", "0") or "0").lstrip("#")  # can be empty, for some reason.
        self.colour: Colour = Colour(int(self._raw_colour, base=16))
        self.color: Colour = self.colour
        self.supporter: bool = kwargs.pop("supporter", False)  # NOTE: unable to get a response from top.gg what this
        # actually is. It isn't premium.
        self.site_mod: bool = kwargs.pop("mod") or kwargs.pop("webMod")  # these are the same thing as far as I'm aware
        self.site_admin: bool = kwargs.pop("admin", False)
        self.certified: bool = kwargs.pop("certified", False)  # if the user has a certified bot

        if kwargs.get("state"):
            self._user: Optional[DiscordUser] = kwargs["state"].get_user(self.id)
        else:
            self._user: Optional[DiscordUser] = None

    def user(self, state=None) -> Optional[DiscordUser]:
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method."""
        if not state:
            return self._user
        if self._user:
            return self._user
        return state.get_user(self.id)


class Bot(UserABC, _ReprMixin):
    """
    Model representing a top.gg bot

    This also conforms with the discord user ABC. See: toppy.models.User
    """

    def __init__(self, **kwargs):
        self.id: int = int(kwargs.pop("id"))
        self.username: str = kwargs.pop("username")
        self.discriminator: str = kwargs.pop("discriminator")
        self.user_avatar: Optional[str] = kwargs.pop("avatar", None)
        self.default_avatar: str = kwargs.pop("defAvatar")
        self.avatar: str = self.user_avatar or self.default_avatar

        self.prefix: str = kwargs.pop("prefix")
        self.short_description: str = kwargs.pop("shortdesc")
        self.long_description: Optional[str] = kwargs.pop("longdesc", None)  # NOTE: this can be empty for some reason
        self.tags: List[str] = kwargs.pop("tags", [])
        self.website: Optional[str] = kwargs.pop("website", None)
        self.support: Optional[str] = kwargs.pop("support", None)
        self.github: Optional[str] = kwargs.pop("github", None)
        self.owners: List[int] = list(map(int, kwargs.pop("owners", [])))
        self.featured_guilds: List[int] = list(map(int, kwargs.pop("guilds", [])))
        self.invite: str = kwargs.pop("invite", None) or invite(str(self.id))
        try:
            self.approved_at: datetime = (
                datetime.strptime("%Y-%m-%dT%H:%M:%S.%fZ", kwargs.pop("date", "")) or datetime.min
            )
        except ValueError:
            self.approved_at = datetime.min
        self.certified: bool = kwargs.pop("certifiedBot", False)
        self.vanity_uri: Optional[str] = kwargs.pop("vanity", None)
        self.all_time_votes: int = kwargs.pop("points", 0)
        self.monthly_votes: int = kwargs.pop("monthlyPoints", 0)
        self.donations_guild: Optional[int] = kwargs.pop("donatebotguildid", None)

        if kwargs.get("state"):
            self._user: Optional[DiscordUser] = kwargs["state"].get_user(self.id)
        else:
            self._user: Optional[DiscordUser] = None

    def user(self, state=None) -> Optional[DiscordUser]:
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method."""
        if not state:
            return self._user
        if self._user:
            return self._user
        return state.get_user(self.id)


class BotStats(_ReprMixin):
    """Model representing 3 fields from /bot/{id}/stats"""

    def __init__(self, **kwargs):
        self.server_count = kwargs.pop("server_count", 0)
        if kwargs.get("shards"):
            self.shards = {shard_id: server_count for shard_id, server_count in enumerate(kwargs["shards"])}
        else:
            self.shards = {0: self.server_count}
        self.shard_count = kwargs.pop("shard_count", 0)
        self.reliable = self.server_count == sum(self.shards.values())
