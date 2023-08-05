import discord
from discord.ext import commands
from core.classes import Cog_Template
from youtube_dl import YoutubeDL
from pytube import Playlist

YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'outtmpl': 'C:\\Users\\User\\Desktop\\discord_BOT-main\\downloads\\%(extractor_key)s\\%(title)s.%(ext)s'}

with YoutubeDL(YDL_OPTIONS) as ydl:
    info = ydl.extract_info("ytsearch:https://www.youtube.com/watch?v=7KfK_hfq6RE")['entries'][0]
    url = 'C:\\Users\\User\\Desktop\\discord_BOT-main\\downloads\\Youtube\\' + info.get('title').replace("|", "_").replace("/", "_") + '.' + info['ext']
print(url)
