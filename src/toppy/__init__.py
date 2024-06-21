try:
    from discord import version_info as discord_version_info
except ImportError as e:
    raise ImportError("A module with the 'discord' namespace is not installed.") from e

from .client import TopGG
from .client import TopGG as Client
from .client import TopGG as DBLClient
from .models import *
