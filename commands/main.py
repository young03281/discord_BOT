import discord
from discord.ext import commands
from core.classes import Cog_Template

class main(Cog_Template):

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(self.bot.latency)

def setup(bot):
   bot.add_cog(main(bot))
