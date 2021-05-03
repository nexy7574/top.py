from argparse import ArgumentParser
import sys
import platform
from re import compile
import os
import datetime

parser = ArgumentParser()

parser.add_argument("-V", "--version", help="Display version information", action="store_true")
args = parser.parse_args()

if args.version:
    print("-" * 15)
    print(f"Python Version: {'.'.join(map(str, sys.version_info[:3]))}")
    print(f"Platform: {sys.platform}", end="")
    print(f" ({platform.platform()}, {platform.version()})")
    with open("./client.py") as client:
        version_regex = compile(r"__version__ = \"(?P<v>[0-9]\.[0-9]{1,2}\.[0-9]+)\"")
        version = version_regex.search(client.read()).group("v")
    print(f"top.py version: {version} (installed: ", end="")

    created_at = datetime.datetime.utcfromtimestamp(os.path.getmtime("./client.py"))
    print(created_at.strftime("%c") + ")")
    print("discord.py version: ", end="")
    try:
        import discord

        print(".".join(map(str, discord.version_info[:3])))
    except ImportError:
        print("Not Installed")
    print("-" * 15)
