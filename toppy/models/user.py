import warnings
from datetime import datetime
from textwrap import shorten
from typing import Optional, List, Tuple

from discord import User as DiscordUser
from discord.colour import Colour
from discord.utils import oauth_url as invite


class _ReprMixin(object):
    """Mixin that provides every model with a humanized repr() string."""

    def __repr__(self):
        """Humanized automatic repr string generator."""
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


def default_avatar_url(discrim: int):
    return f"https://cdn.discordapp.com/embed/avatars/{discrim % 5}.png"


def calculate_avatar_url(user_id: int, _hash: str):
    return f"https://cdn.discordapp.com/avatars/{user_id}/{_hash}.webp"


class WeakAttr(dict, _ReprMixin):
    """A simple class that takes a dictionary and allows fetching of items through attributes."""

    def __getattr__(self, item):
        result = self.get(item)
        if result:
            return result
        raise AttributeError("WeakAttr has no attribute '%s'" % item)


class UserABC(_ReprMixin):
    """ABC that kinda conforms to discord.py's user class."""

    id: int
    username: str
    discriminator: str
    user_avatar: str
    default_avatar: str
    avatar: str

    def user(self, state=None):
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method."""
        raise NotImplementedError


class SimpleUser(_ReprMixin):
    """A model representing the "simple user" object returned by /bots/{id}/votes."""

    def __init__(self, **kwargs):
        self.id: int = int(kwargs.pop("id"))
        self.discriminator: str = kwargs.pop("discriminator", "#0000")
        self.username: str = kwargs.pop("username")
        self.avatar: Optional[str] = calculate_avatar_url(
            self.id, int(self.discriminator[1:]), kwargs.pop("avatar", None)
        )


class User(UserABC, _ReprMixin):
    """
    Model representing a top.gg user's account.

    This class conforms to the discord.User ABC.
    """

    def __init__(self, **kwargs):
        self._id: int = int(kwargs.pop("id"))
        self._username: str = kwargs.pop("username")
        self._discriminator: str = kwargs.pop("discriminator")
        self._default_avatar: str = default_avatar_url(int(self._discriminator))
        self._avatar: str = kwargs.pop("avatar", None)
        self._bio: Optional[str] = kwargs.pop("bio", None)
        self._banner_url: Optional[str] = kwargs.pop("banner", None)
        self._socials: WeakAttr = WeakAttr(kwargs.pop("social", {}))
        self._raw_colour = (kwargs.get("color", "0") or "0").lstrip("#")  # can be empty, for some reason.
        self._colour: Colour = Colour(int(self._raw_colour, base=16))
        self._supporter: bool = kwargs.pop("supporter", False)  # NOTE: unable to get a response from top.gg what this
        # actually is. It isn't premium.
        self._site_mod: bool = kwargs.pop("mod") or kwargs.pop("webMod")  # these are the same thing as far as I'm aware
        self._site_admin: bool = kwargs.pop("admin", False)
        self._certified: bool = kwargs.pop("certified", False)  # if the user has a certified bot

        if kwargs.get("state"):
            self._user: Optional[DiscordUser] = kwargs["state"].get_user(self.id)
        else:
            self._user: Optional[DiscordUser] = None

    @property
    def id(self) -> int:
        """The user's user ID."""
        return self._id

    @property
    def name(self) -> str:
        """The user's username."""
        return self._username

    @property
    def discriminator(self) -> str:
        """The user's #0000 discriminator"""
        return self._discriminator

    @property
    def avatar_url(self) -> str:
        """This returns the user's resolved avatar URL.

        If the user doesn't have an avatar, this will return their default one."""
        if self._avatar:
            return calculate_avatar_url(self.id, self._avatar)
        return default_avatar_url(int(self.discriminator))

    @property
    def bio(self) -> str:
        """The user's bio section on top.gg"""
        return self._bio

    @property
    def banner_url(self) -> str:
        """The user's banner URL on their top.gg profile"""
        return self._banner_url

    @property
    def colour(self) -> Colour:
        """The user's preferred navigation colour.

        There is an alias for this under toppy.models.User.color

        :returns: discord.Colour - the resolved colour"""
        return self._colour

    @property
    def color(self) -> Colour:
        """Alias for toppy.models.User.colour"""
        return self.colour

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


class BotSearchResults(_ReprMixin):
    """A"""

    # We love linting.
    results: Tuple[Bot]
    limit: int
    offset: int
    count: int
    total: int

    def __init__(self, *results: Bot, limit: int, offset: int):
        self.results = results
        self.limit = limit
        self.offset = offset
        self.count = len(results)
        self.total = self.count

    def __getitem__(self, item):
        raise DeprecationWarning(
            "fetch_bots no-longer returns a dictionary, and it looks like you treat it "
            "as such. You should now use iter(results) (to iterate results) or use one of "
            "the attributes."
        )

    def __iter__(self):
        return self.results


class BotStats(_ReprMixin):
    """Model representing 3 fields from /bot/{id}/stats"""

    def __init__(self, **kwargs):
        self.server_count: int = kwargs.pop("server_count", 0)
        if kwargs.get("shards"):
            self.shards = {shard_id: server_count for shard_id, server_count in enumerate(kwargs["shards"])}
        else:
            self.shards = {0: self.server_count}
        self.shard_count: int = kwargs.pop("shard_count", 0)
        self.reliable: bool = self.server_count == sum(self.shards.values())
