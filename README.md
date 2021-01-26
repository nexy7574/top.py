# Top.py
![](https://img.shields.io/github/issues/dragdev-studios/top.py?style=flat-square)
![](https://img.shields.io/github/issues-pr/dragdev-studios/top.py?style=flat-square)
![](https://img.shields.io/pypi/v/top.py?style=flat-square)
![](https://img.shields.io/pypi/dw/top.py?style=flat-square)
![](https://img.shields.io/badge/code%20style-black-black?style=flat-square)
![](https://img.shields.io/badge/top.gg%20api%20coverage-100%25-blue?style=flat-square)


A modern python module wrapper for the official [top.gg API](https://top.gg/api/docs).

**THIS MODULE IS NOT ENDORSED BY TOP.GG.** Their official package is [here](https://pypi.org/project/dblpy).


## Installation
### Dev
*without pip*
```shell
git clone https://github.com/dragdev-studios/top.py
cd top.py
python3 setup.py build && python3 setup.py install
```
*with pip*
```shell
pip install git+https://github.com/dragdev-studios/top.py
```

### Stable
pip
```shell
pip install top.py
```

git
```shell
# replace curl with wget, or whatever you use to make web requests
curl https://github.com/dragdev-studios/top.py/archive/<version>.tar.gz > top.py.tar.gz
tar -xf top.py.tar.gz
cd top.py
python3 setup.py install
```

## Usage
*Documentation can be found in the github's [wiki](https://github.com/dragdev-studios/top.py/wiki)*

```python
from toppy.client import TopGG
from discord.ext import commands


class TopGGCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.top_gg = TopGG(
            self.bot,
            token="example-token-please-replace"
        )

    @commands.command()
    @commands.cooldown(1, 5)  # this can be changed, however over 60 requests per minute will get you blocked.
    async def voted(self, ctx):
        """Tells you if you've voted for me!"""
        has_voted = await self.top_gg.upvote_check(ctx.author.id)
        return await ctx.send("You have voted for me <3" if has_voted else "No, you haven't. Please vote!")

def setup(bot):
    bot.add_cog(TopGGCog(bot))
```
The above example will create a cog that will have a `top_gg` attribute and a `voted` command, which tells the user if
they've voted.

```python
TopGG(
    bot,
    token="...",
    autopost=False
)
```
This example will disable the internal autopost task (which posts your server count evey 30 minutes)
