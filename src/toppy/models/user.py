from dataclasses import dataclass
from typing import Optional


__all__ = (
    "Social",
    "User"
)


@dataclass
class Social:
    """Represents the dictionary of social links of a user"""
    youtube: Optional[str] = None
    reddit: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None


@dataclass
class User:
    """
    Represents a single user on top.gg

    .. note:
        A user represents a User account in top.gg. It is not associated with any other platform like Discord.

    See Also: https://docs.top.gg/docs/API/user#structure
    """
    id: str
    """ The ID of the user"""

    username: str
    """ The username of the user"""

    discriminator: str
    """ The discriminator of the user"""

    defAvatar: str
    """The cdn hash of the user's avatar if the user has none"""

    social: Social
    """The social usernames of the user"""

    supporter: bool
    """The supporter status of the user"""

    certifiedDev: bool
    """The certified developer status of the user"""

    mod: bool
    """The moderation status of the user"""

    webMod: bool
    """The web moderation status of the user"""

    admin: bool
    """The admin status of the user"""

    bio: Optional[str] = None
    """The bio of the user"""

    banner: Optional[str] = None
    """The banner URL of the user"""

    color: Optional[str] = None
    """The custom hex color of the user (not guaranteed to be valid hex)"""
    # Top.gg, why can you not validate its hex? do you validate it at all yourselves?
