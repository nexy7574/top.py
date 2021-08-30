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
        # According to peers this repr method is bad
        # (ref: https://discord.com/channels/264445053596991498/272764566411149314/820678536079212615)
        # So maybe we can tidy it up at some point?
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


# The following two methods are a bit pointless, they're only used a couple times.
def default_avatar_url(discrim: int):
    return f"https://cdn.discordapp.com/embed/avatars/{discrim % 5}.png"


def calculate_avatar_url(user_id: int, discrim: int, _hash: str):
    if not _hash:
        return default_avatar_url(discrim)
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
    """
    A model representing the "simple user" object returned by /bots/{id}/votes.

    Attributes:
        id: :class:`py:int`
            The user's ID
        discriminator: :class:`py:str`
            The user's discriminator (prefixed with #)
        username: :class:`py:str`
            the user's username
        avatar: Optional[:class:`py:str`]
            The user's avatar URL
    """

    def __init__(self, **kwargs):
        self.id: int = int(kwargs.pop("id"))
        self.discriminator: str = kwargs.pop("discriminator", "#0000")
        self.username: str = kwargs.pop("username")
        self.avatar: Optional[str] = calculate_avatar_url(
            self.id, int(self.discriminator[1:]), kwargs.pop("avatar", None)
        )


class Socials(_ReprMixin):
    """
    Model containing every social link on a top.gg user's profile.

    .. warning::
        This class does not resolve URLs.

    Attributes:
        youtube: Optional[:class:`py:str`]
        reddit: Optional[:class:`py:str`]
        instagram: Optional[:class:`py:str`]
        github: Optional[:class:`py:str`]
        twitter: Optional[:class:`py:str`]

    """

    def __init__(self, **kwargs):
        # NOTE:
        # We don't resolve URLs here. We're gonna leave that up to the user.
        self.youtube = kwargs.pop("youtube", None)
        self.reddit = kwargs.pop("reddit", None)
        self.instagram = kwargs.pop("instagram", None)
        self.github = kwargs.pop("github", None)
        self.twitter = kwargs.pop("twitter", None)


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
        self._socials = kwargs.pop("social", {})
        self._raw_colour = (kwargs.get("color", "0") or "0").lstrip("#")  # can be empty, for some reason.
        self._colour: Colour = Colour(int(self._raw_colour, base=16))
        self._supporter: bool = kwargs.pop("supporter", False)
        self._site_mod: bool = kwargs.pop("mod") or kwargs.pop("webMod")  # these are the same thing as far as I'm aware
        self._site_admin: bool = kwargs.pop("admin", False)
        self._certified: bool = kwargs.pop("certified", False)  # if the user has a certified bot
        if kwargs.get("state"):
            self._user: Optional[DiscordUser] = kwargs["state"].get_user(self.id)
        else:
            self._user: Optional[DiscordUser] = None

    @property
    def socials(self) -> Socials:
        """An object containing the user's social links."""
        return Socials(**self._socials)

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

        :returns: discord.Colour - the resolved colour
        :rtype: :class:`discord:discord.Colour`"""
        return self._colour

    @property
    def color(self) -> Colour:
        """Alias for toppy.models.User.colour"""
        return self.colour

    def user(self, state=None) -> Optional[DiscordUser]:
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method.

        :rtype: Optional[:class:`discord:discord.User`]"""
        if not state:
            return self._user
        if self._user:
            return self._user
        return state.get_user(self.id)


class Bot(UserABC, _ReprMixin):
    """
    Model representing a top.gg bot

    This also conforms with the discord user ABC. See: toppy.models.User

    Attributes:
        id: :class:`py:int`
            The bot's ID
        discriminator: :class:`py:str`
            The bot's discriminator (prefixed with #)
        username: :class:`py:str`
            the bot's username
        avatar: :class:`py:str`
            The bot's avatar hash
        user_avatar: Optional[:class:`py:str`]
            The bot's custom avatar hash
        default_avatar: :class:`py:str`
            The bot's default avatar hash
        prefix: :class:`py:str`
            The bot's prefix
        short_description: :class:`py:str`
            The bot's short description on top.gg
        long_description: :class:`py:str`
            The bot's long description on top.gg
        tags: :class:`py:List`[:class:`py:str`]
            A list of tags the bot uses on top.gg
        website: Optional[:class:`py:str`]
            The bot's website. Can be None.
        support: Optional[:class:`py:str`]
            The bots support server URL. Can be None
        github: Optional[:class:`py:str`]
            The bot's github repo page URL. Can be None.
        owners: :class:`py:List`[:class:`py:int`]
            A list of owner IDs that own this bot.
        featured_guilds: :class:`py:List`[:class:`py:int`]
            A list of featured guild IDs that are used on the bot's top.gg page
        invite: :class:`py:str`
            The bot's invite URL

            .. danger::
                This URL is not always a discord.com URL. If you are making requests to it, just be aware.

        approved_at: :class:`py:datetime.datetime`
            The datetime that this bot was approved at on top.gg

            .. note::
                This can sometimes fail to resolve the given timestamp, and defaults to :obj:`py:datetime.datetime.min`.
        certified: :class:`py:bool`
            Boolean indicating if this bot is certified on top.gg
        vanity_uri: Optional[:class:`py:str`]
            This bot's vanity endpoint on top.gg
        all_time_votes: :class:`py:int`
            The total number of votes this bot received the entire time it has been on top.gg
        monthly_votes: :class:`py:int`
            The total number of votes the bot got this month
        donations_guild: Optional[`py:int`]
            The server ID for donations using donatebot
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
    """
    A container for search results.

    Attributes:
        results: :class:`py:tuple`[:class:`toppy.models.Bot`]
            A tuple containing every found bot
        limit: :class:`py:int`
            The limit used
        offset: :class:`py:int`
            The offset used
        count: :class:`py:int`
            The total number of bots found
        total: :class:`py:int`
            An alias for ``count``
    """

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
