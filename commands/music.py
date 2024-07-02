import discord
from discord.ext import commands
from core.classes import Cog_Template
from yt_dlp import YoutubeDL
from pytube import Playlist

class music_Bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True', 'outtmpl': './downloads/%(extractor_key)s/%(title)s.%(ext)s'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None
        self.is_repeat = 0
        #0 = no
        #1 = first
        #2 = queue
        self.current_song = ''
        self.repeat_url = []
        global m_url

     #searching the item on youtube

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download = False)['entries'][0]
                url = "./downloads/" + info.get("extractor") + "/" + info.get('title').replace("|", "_").replace("/", "_") + '.' + info['ext']
            except Exception: 
                return False
                
        return {'source': info['url'], 'title': info['title']} #info['formats'][0]['url']

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']
            self.current_song  = self.music_queue[0][0]['title']

            if self.repeat_url == '' :
                self.repeat_url = self.music_queue[0]
                self.current_song = self.music_queue[0][0]['title']
            
            #try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                voice = ctx.author.voice.channel
                if voice.connect() == None:
                    self.vc = await self.music_queue[0][1].connect()

                    #in case we fail to connect
                    if self.vc == None:
                        await ctx.send("Could not connect to the voice channel")
                        return
                else :
                    await ctx.send("Connected to voice channel")
                    if ctx.guild.voice_client :
                        await ctx.guild.voice_client.disconnect()
                    self.vc = await self.music_queue[0][1].connect()
                    if self.vc == None:
                        await ctx.send("Could not connect to the voice channel")
                        return
            else:
                await self.vc.move_to(self.music_queue[0][1])
            try:
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            except Exception as e:
                print(e)
        else:
            await ctx.send("theres no songs in queue")
            self.is_playing = False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            self.repeat_url = self.music_queue[0]
            self.music_queue.pop(0)

            if len(self.music_queue) != 0 : 
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']
            else :
                self.is_playing = False
                return
            
            if self.is_repeat == 1 : 
                self.music_queue.insert(0, self.repeat_url)
                self.repeat_url = self.music_queue[0]
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']

            if self.is_repeat == 2 :
                self.music_queue.append(self.repeat_url)
                self.repeat_url = self.music_queue[0]
                m_url = self.music_queue[0][0]['source']
                self.current_song = self.music_queue[0][0]['title']
            
            self.vc.play(discord.FFmpegPCMAudio(source= m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        
        voice = ctx.author.voice
        if voice is None:
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                if "playlist" in query :
                    await ctx.send("it's a playlist")
                    global p 
                    p = Playlist(query)
                    psong = []
                    j = 0
                    for i in p.video_urls:
                        urls = self.search_yt(i)
                        if type(urls) == type(True):
                            await ctx.send("cant download the song. maybe it's 不公開")
                            continue
                        psong.append(urls)
                        j += 1
                        if j > 19:
                            await ctx.send("theres a 20 song limit and you reach it ")
                            break
                    for i in psong :
                        self.music_queue.append([i, voice.channel])
                    await ctx.send("Songs added to the queue")
                    if self.is_playing == False:
                        await self.play_music(ctx)
                else:
                    await ctx.send("cant downlaod")
            else:
                self.music_queue.append([song, voice.channel])
                await ctx.send("Song added to the queue")
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", aliases=["pa"], help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            await ctx.send("paused")
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

    @commands.command(name = 'repeat', aliases=["re"], help="repeat the song")
    async def repeat(self, ctx, *args):
        str_args = ''.join(args)
        if str_args != '': int_args = int(str_args)
        else: int_args = ''
        if int_args == 0:
            self.is_repeat = 0
            await ctx.send('stop repeating')
        elif int_args == 1:
            self.is_repeat = 1
            await ctx.send('currently repeating song:%s' %self.music_queue[0][0]['title'] )
        elif int_args == 2:
            self.is_repeat = 2
            retval = ""
            for i in range(0, len(self.music_queue)):
                retval += f'{i+1}' + ". " + self.music_queue[i][0]['title'] + "\n"
            await ctx.send(f'currently repeating queue :\n{retval}')
        else:
            if self.is_repeat == 2:
                self.is_repeat = 0
                await ctx.send('stop repeating')
            else:   
                if self.is_repeat == 0:
                    self.is_repeat = 1
                    await ctx.send('currently repeating song:%s' %self.music_queue[0][0]['title'] )
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
            if len(self.music_queue)  > 1 : 
                await ctx.send('skipping current song:%s \n going to play:%s' %(self.current_song, self.music_queue[1][0]['title']) )
            else :
                await ctx.send('skipping current song:%s' %self.current_song)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            if (i == 0) :
                retval += 'current song :' + self.music_queue[i][0]['title'] + "\n"
            else :
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
        self.music_queue = []
        await ctx.guild.voice_client.disconnect()

    @commands.command(name="join", aliases=["j"], help="Let the bot join the vc")
    async def join(self, ctx):
        voice = ctx.author.voice
        if voice is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            await voice.channel.connect()

async def setup(bot):
    await bot.add_cog(music_Bot(bot))