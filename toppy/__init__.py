from sys import version_info as python_version_info
from discord import version_info as discord_version_info
from warnings import warn

if python_version_info <= (3, 6, 0) and discord_version_info >= (1, 8, 0):
    warn(
        "Python 3.6 is no-longer supported by discord.py. Please update your python version.\n"
        "This module will cease support when discord.py 2.0.0 is released.",
        DeprecationWarning,
    )

from .models import large_widget, small_widget, ColourOptions, ColourOptions as ColorOptions, Bot, User
from .client import TopGG, TopGG as Client, TopGG as DBLClient
