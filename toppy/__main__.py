from argparse import ArgumentParser
import sys
import platform
from re import compile
from subprocess import run, PIPE, DEVNULL
import datetime
from pathlib import Path

parser = ArgumentParser()

CLIENT = Path(__file__).parent / "client.py"

parser.add_argument("-V", "--version", help="Display version information", action="store_true")
args = parser.parse_args()

if args.version:
    pip_version = run(("pip", "--version"), stdout=PIPE, stderr=DEVNULL).stdout.split(b" ")[1].decode()
    print("-" * 15)
    print(f"Python Version: {'.'.join(map(str, sys.version_info[:3]))} (pip {pip_version})")
    print(f"Platform: {sys.platform}", end="")
    print(f" ({platform.platform()}, {platform.version()})")
    print(f"Install Location:", Path(__file__).parent.resolve(), " (CWD: %s)" % Path.cwd())
    with open(CLIENT) as client:
        version_regex = compile(r"__version__ = \"(?P<v>[0-9]\.[0-9]{1,2}\.[0-9]+)\"")
        version = version_regex.search(client.read()).group("v")
    print(f"top.py version: {version} (installed at: ", end="")

    created_at = datetime.datetime.utcfromtimestamp(CLIENT.stat().st_mtime)
    print(created_at.strftime("%c") + ")")
    print("discord.py version: ", end="")
    try:
        import discord

        print(".".join(map(str, discord.version_info[:3])))
    except ImportError:
        print("Not Installed")
    print("-" * 15)
