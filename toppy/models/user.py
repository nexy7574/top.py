from discord.abc import User as _UserABC
from discord import User as DiscordUser
from typing import Optional, List
from discord.colour import Colour
from discord.utils import oauth_url as invite
from datetime import datetime


class WeakAttr(dict):
    """A simple class that takes a dictionary and allows fetching of items through attributes."""

    def __getattr__(self, item):
        result = self.get(item)
        if result:
            return result
        raise AttributeError("WeakAttr has no attribute '%s'" % item)


class UserABC:
    id: int
    username: str
    discriminator: str
    user_avatar: str
    default_avatar: str
    avatar: str


class User(UserABC):
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

    def user(self, state = None) -> Optional[DiscordUser]:
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method."""
        if not state:
            return self._user
        if self._user:
            return self._user
        return state.get_user(self.id)


class Bot(UserABC):
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
        self.tags: List[str] = kwargs.pop("tags")
        self.website: Optional[str] = kwargs.pop("website", None)
        self.support: Optional[str] = kwargs.pop("support", None)
        self.github: Optional[str] = kwargs.pop("github", None)
        self.owners: List[int] = list(map(int, kwargs.pop("owners", [])))
        self.featured_guilds: List[int] = list(map(int, kwargs.pop("guilds", [])))
        self.invite: str = kwargs.pop("invite", None) or invite(str(self.id))
        try:
            self.approved_at: datetime = datetime.strptime(
                "%Y-%m-%dT%X%fZ",
                kwargs.pop("date", "")
            ) or datetime.min
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

    def user(self, state = None) -> Optional[DiscordUser]:
        """Gets the current discord user object from the top.gg user object.

        state can be the bot/client instance, or anything with a get_user method."""
        if not state:
            return self._user
        if self._user:
            return self._user
        return state.get_user(self.id)
