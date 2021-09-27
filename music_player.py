import nextcord
from nextcord.ext import commands
from youtube_dl import YoutubeDL

import config

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Determines whether or not the bot is currently playing.
        # If music is already playing and a new play request is received, it will instead be queued.
        self.is_playing = False

        self.music_queue = [] # [song, channel]
        self.YDL_OPTIONS = {
            "format"     : "bestaudio",
            "noplaylist" : "True"
        }
        self.FFMPEG_OPTIONS = {
            "before_options" : "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options"        : "-vn",
            "executable"     : config.FFMPEG_PATH
        }
        self.vc = "" # Stores the current channel

    def search_yt(self, item):
        """ Searches YouTube for the requested search term, returns the first result only."""
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        return { "source" : info["formats"][0]["url"],
                 "title"  : info["title"]}

    def play_next(self):
        if len(self.music_queue) > 0: # If there's music waiting in the queue...
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']  # ...get the first URL...
            self.music_queue.pop(0)                   # ...remove the first element from the queue...

            # ...then play the music in the current VC!
            # Once the music is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.vc.play(nextcord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False # Stop playing music.

    async def play_music(self):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]['source']

            # Try to connect to the VC if not connected
            if self.vc == "" or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()
            else:
                self.vc = await self.bot.move_to(self.music_queue[0][1])

            print(self.music_queue)
            self.music_queue.pop(0)

            self.vc.play(nextcord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

        else:
            self.is_playing = False # Stop playing music.


    @commands.command()
    async def play(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel

        if voice_channel is None:
            await ctx.send("Connect to a voice channel first, _then_ issue the command!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Unable to play song due to incorrect video format.")
            else:
                await ctx.send("Song added to queue!")
                self.music_queue.append([song, voice_channel])

                if self.is_playing == False:
                    await self.play_music()

    @commands.command()
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            retval += self.music_queue[i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("Nothing queued up at the moment!")

    @commands.command()
    async def skip(self, ctx):
        if self.vc != "":
            self.vc.stop()
            await self.play_music()
