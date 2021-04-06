# Examples
These are a bunch of example samples that you can use in your own code,
with a bit of modification of course.

However, there is no one-size-fits-all for this - please always use your own code
rather than relying on copy+paste+tweaks.

Furthermore, **this is a simple list**. We do not list **every possibility** within here,
just something that can get you running.

## Standalone Cog

* Requires: discord.ext.commands, Bot (!Client)

```python
from toppy.client import TopGG
from discord.ext import commands

TOP_GG_API_KEY = "foobar"
# Top.py version: 1.1.1


class TopGGCog(commands.Cog):
    """Commands related to top.gg"""
    def __init__(self, bot):
        self.bot = bot
        self.top_gg = TopGG(
            self.bot,
            token=TOP_GG_API_KEY,
            autopost=True  # True is default.
        )
    
    def cog_unload(self):
        self.bot.loop.create_task(self.top_gg.session.close())
        # ^ Avoid unclosed client session warnings
        
        # While you don't need to do this (it's handled automatically 
        # when the client is destroyed), there's no reason not to.
        self.top_gg.autopost.stop()
    
    @commands.command()
    async def vote(self, ctx: commands.Context):
        """Gives you a link to vote."""
        if await self.top_gg.has_upvoted(ctx.author.id):
            await ctx.send("You already voted!")
        else:
            await ctx.send(self.top_gg.vote_url)
            
    @commands.command()
    async def invite(self, ctx: commands.Context):
        """Sends you an invite link to invite me!"""
        await ctx.send(self.top_gg.invite_url)
        

def setup(bot):
    bot.add_cog(TopGGCog(bot))

```


## In runtime file

```python
from toppy.client import TopGG
from discord.ext import commands


bot = commands.Bot("!")
bot.top_gg = TopGG(bot, token="...")

@bot.listen("on_guild_post")
async def stats_posted(data: dict):
    print(f"Posted {data['server_count']} servers to top.gg")
    

bot.run("token")
```
