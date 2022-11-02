import discord
from discord.ext import commands
from core.classes import Cog_Template

class main_Cog(Cog_Template):

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'{round((self.bot.latency)*1000)}(ms)')

async def setup(bot):
   await bot.add_cog(main_Cog(bot))
