import discord
from discord.ext import commands
import json
import os

with open('setting.json', 'r', encoding='UTF8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.$',intents=intents)

@bot.event
async def  on_ready():
    print(">>Bot Is Online<<")
    for Filename in os.listdir('./commands'):
        if Filename.endswith('.py'):
           await bot.load_extension(f'commands.{Filename[:-3]}')

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(int(jdata['Welcome_Channel_ID']))
    await channel.send(f'{member} join')
    print(f'{member} join')

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(int(jdata['Leave_Channel_ID']))
    await channel.send(f'{member} leave')
    print(f'{member} leave')

async def load_extensions():
    for Filename in os.listdir('./commands'):
        if Filename.endswith('.py'):
            bot.load_extension(f'commands.{Filename[:-3]}')

@bot.command()
async def load(ctx, ext):
    bot.load_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} loaded successfully.')    

@bot.command()
async def unload(ctx, ext):
    bot.unload_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} unloaded successfully.')

@bot.command()
async def reload(ctx, ext):
    bot.reload_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} reloaded successfully.')

if __name__ == '__main__':
    bot.run(jdata['TOKEN'])