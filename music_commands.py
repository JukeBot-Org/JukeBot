import nextcord as discord
from nextcord.ext import commands
from youtube_dl import YoutubeDL
from colorama import Fore, Style
import datetime

import config
from embed_dialogs import DialogBox

def dbug(foo):
    return "`{}`".format(foo)

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Determines whether or not the bot is currently playing.
        # If music is already playing and a new play request is received, it will instead be queued.
        self.is_playing = False

        self.music_queue = [] # [song data, voice channel to join when played]
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

# ===================== FUNCTIONS ====================== #
    def search_yt(self, item):
        """ Searches YouTube for the requested search term, returns the first result only."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)["entries"][0]
            except Exception:
                print("====================================\n" + Style.RESET_ALL)
                return False
        print("====================================\n" + Style.RESET_ALL)
        return { "source"   : info["formats"][0]["url"],
                 "title"    : info["title"],
                 "thumb"    : info["thumbnail"],
                 "duration" : str(datetime.timedelta(seconds=info["duration"]))
               }

    async def play_audio(self, ctx):
        if len(self.music_queue) > 0: # If there are tracks in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"]

            if self.vc == "": # If not in a voice channel currently...
                self.vc = await self.music_queue[0]["voice_channel"].connect()

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False

    def play_next(self, ctx):
        if len(self.music_queue) > 0: # If there's music waiting in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"] # ...get the first URL...
            self.music_queue.pop(0)                                # ...remove the first element from the queue...

            # ...then play the music in the current VC!
            # Once the music is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.vc.play(discord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False # Stop playing music.

# ====================== COMMANDS ====================== #

    @commands.command()
    async def play(self, ctx, *args):
        """Plays a song in the voice channel that you're currently in.
        If there's music currently playing, the song is instead added to the queue.
        Accepts YouTube links, search terms, and Spotify links (SPOTIFY NOT YET WORKING, STILL IN TESTING).

        **Examples**

        `<prefix>play https://www.youtube.com/watch?v=dQw4w9WgXcQ`

        `<prefix>play earth wind and fire september`

        `<prefix>play https://open.spotify.com/track/3iVcZ5G6tvkXZkZKlMpIUs?si=e84140d21af44958` (SPOTIFY NOT YET WORKING, STILL IN TESTING)
        """
        query = " ".join(args)

        if ctx.author.voice is None:

            await ctx.send(embed=DialogBox("Warn", "Hang on!", "Connect to a voice channel first, _then_ issue the command."))
            return

        voice_channel = ctx.author.voice.channel # Set which voice channel to join later on in the command

        song_data = self.search_yt(query)
        if song_data == False:

            await ctx.send(embed=DialogBox("Error", "Unable to play song", "Incorrect video format or link type."))
            return

        self.music_queue.append({
            "song_data"     : song_data,
            "voice_channel" : voice_channel
        })

        # Start preparing the dialog to be posted.

        if self.is_playing == False:
            reply = DialogBox("Playing", f"Now playing: {song_data['title']}")
        else:
            reply = DialogBox("Queued", f"Adding to queue: {song_data['title']}")

        reply.set_image(url=song_data["thumb"])
        reply.add_field(name="Duration" , value=song_data["duration"], inline=True)

        await ctx.send(embed=reply)

        if self.is_playing == False:
            await self.play_audio(ctx)
        else:
            await ctx.send(ctx.author.voice.channel)

    @commands.command()
    async def queue(self, ctx):
        """Displays the queue of music waiting to be played"""
        queue = "".join([f"{track+1} — {self.music_queue[track]['song_data']['title']}\n" for track in range(0, len(self.music_queue))]) # God this sucks
        if self.vc == "":
            reply = embed=DialogBox("Warn", "Hang on!", "Connect to a voice channel first, _then_ issue the command.")
        else:
            reply = embed=DialogBox("Queued", "Queued music", f"`{queue}`")

        await ctx.send(embed=reply)

    @commands.command()
    async def skip(self, ctx):
        """Skips the song currently playing.
        If there are still tracks in the queue, the next one will automatically play.
        """
        if self.vc == "":
            reply = DialogBox("Warn", "Hang on!", "JukeBot is currently not playing; there's nothing to skip.")
        else:
            reply = DialogBox("Skip", "Skipped track")
            self.vc.stop()
            await self.play_audio(ctx)

        await ctx.send(embed=reply)

    @commands.command()
    async def clear(self, ctx):
        """Removes all songs from the queue.
        Does not affect the currently-playing song.
        """
        if self.music_queue == []:
            reply = DialogBox("Warn", "Hang on!", "The queue is already empty.")
        else:
            self.music_queue = []
            reply = DialogBox("Queued", "Cleared queue")

        await ctx.send(embed=reply)
