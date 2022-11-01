import discord
from discord.ext import commands
from core.classes import Cog_Template

class main(Cog_Template):

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(self.bot.latency)

async def setup(bot):
   await bot.add_cog(main(bot))
