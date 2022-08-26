from sys import version_info as python_version_info

try:
    from discord import version_info as discord_version_info
except ImportError as e:
    raise ImportError("A module with the 'discord' namespace is not installed.") from e
from warnings import warn

if python_version_info <= (3, 6, 0) and discord_version_info >= (1, 8, 0):
    warn(
        "Python 3.6 is no-longer supported by discord.py. Please update your python version.\n"
        "This module will cease support when discord.py 2.0.0 is released.",
        DeprecationWarning,
    )

from .client import TopGG
from .client import TopGG as Client
from .client import TopGG as DBLClient
from .models import *
from .server import *
