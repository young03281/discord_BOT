import discord
from discord.ext import commands
from core.classes import Cog_Template
from youtube_dl import YoutubeDL
import ffmpeg

class music_Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None
        self.is_repeat = 0
        self.current_song = ''
        self.repeat_url = []

     #searching the item on youtube
     
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.music_queue.pop(0)
            global m_url
            
            if len(self.music_queue) != 0 : 
                self.repeat_url = self.music_queue[0]
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']
            
            if self.is_repeat == 1 : 
                self.music_queue.extend(self.repeat_url)
                self.repeat_url = self.music_queue[0]
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']

            if self.is_repeat == 2 :
                self.music_queue.append(self.repeat_url)
                self.repeat_url = self.music_queue[0]
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']
            
            #remove the first element as you are currently playing it
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    # infinite loop checking 
    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            
            self.repeat_url = self.music_queue[0]
            global m_url
            m_url = self.music_queue[0][0]['source']
            self.current_song = self.music_queue[0][0]['title']
            
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice = ctx.author.voice
        if voice is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice.channel])
                
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = 'repeat', aliases=["re"], help="repeat the current song")
    async def repeat(self, ctx, *args):
        if self.is_repeat == 2: 
            self.is_repeat = 0
            await ctx.send('stop repeating')
        else:   
            if self.is_repeat == 0:
                self.is_repeat = 1
                await ctx.send('currently repeating song:%s' %self.current_song )
            else : 
                self.is_repeat = 2
                retval = ""
                for i in range(0, len(self.music_queue)):
                    retval += f'{i+1}' + ". " + self.music_queue[i][0]['title'] + "\n"
                await ctx.send(f'currently repeating queue :\n{retval}')
                    


    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            self.music_queue.pop(0)
            #try to play next in the queue if it exists
            await self.play_music(ctx)


    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            # display a max of 5 songs in the current queue
            retval += f'{i+1}' + ". " + self.music_queue[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()

async def setup(bot):
    await bot.add_cog(music_Bot(bot))