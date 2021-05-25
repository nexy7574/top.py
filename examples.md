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

## Webhook
### Code:
```python
from toppy.models.webhooks import Vote
from toppy.server import create_server
from discord.ext import commands

bot = commands.Bot("!")

webhook_host = "0.0.0.0"
webhook_port = 2048  # set to whatever port you've forwarded
webhook_path = "/vote"  # http://host:port/[path] (this examples would be :port/vote)
webhook_auth = "..."  # This is the authorisation sent by top.gg to verify that their request is real.
                      # if you want to disable this (don't), you can set it to `None`.

bot.top_gg_server = bot.loop.run_until_complete(  # we have to use run until complete as
    create_server(  # this function right here is an async one.
        bot,
        host=webhook_host,
        port=webhook_port,
        path=webhook_path,
        auth=webhook_auth
    )
)

@bot.event
async def on_vote(vote: Vote):
    print(f"New vote from {vote.user.id}!")

bot.run("token")
```

This will look like the below screenshot on top.gg:

![well then, your image loaded well didn't it](https://cdn.discordapp.com/attachments/635528394033070090/846768933981126706/unknown.png)
