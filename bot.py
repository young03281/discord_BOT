import discord
from discord.ext import commands
import json
import os

with open('setting.json', 'r', encoding='UTF8') as jfile:
    jdata = json.load(jfile)

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='.$',intents=intents)

text_channel_list = []

help_message = """
```
General commands:
.$help - displays all the available commands
.$play(p) <keywords> - finds the song on youtube and plays it in your current channel. Will resume playing the current song if it was paused
.$queue(q) - displays the current music queue
.$skip(s) - skips the current song being played
.$clear(c) - Stops the music and clears the queue
.$leave(l) - Disconnected the bot from the voice channel
.$pause(p) - pauses the current song being played or resumes if already paused
.$resume(r) - resumes playing the current song
.$repeat(re) - repeat the current song

for repeat: 0 for stop repeating. 1 for repeating song. 2 for repeat queue. 
```
"""

bot.remove_command('help')

async def send_to_all(msg):
    for text_channel in text_channel_list:
        await text_channel.send(msg)

@bot.event
async def  on_ready():
    print(">>Bot Is Online<<")
    await send_to_all(help_message)
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

@bot.command()
async def load(ctx, ext):
    bot.load_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} loaded successfully.')    

@bot.command()
async def unload(ctx, ext):
    bot.unload_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} unloaded successfully.')

@bot.command(name="help", help="Displays all the available commands")
async def help(ctx):
    await ctx.send(help_message)

@bot.command()
async def reload(ctx, ext):
    bot.reload_extension(f'Cog.{ext}')
    await ctx.send(f'{ext} reloaded successfully.')

if __name__ == '__main__':
    bot.run(jdata['TOKEN'])