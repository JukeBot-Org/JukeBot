import nextcord as discord
from nextcord.ext import commands
from youtube_dl import YoutubeDL
from colorama import Fore, Style
import datetime

import json

import config
from embed_dialogs import dialogBox
import data_structures as JukeBot

class Music(commands.Cog):
    """The cog that handles all of the music commands and audio-playing operations."""
    def __init__(self, client):
        self.client = client

        # Determines whether or not the bot is currently playing.
        # If music is already playing and a new play request is received, it will instead be queued.
        self.is_playing = False

        self.music_queue = [] # [song data, voice channel to join when played]
        self.YDL_OPTIONS    = {"format"         : "bestaudio",
                               "noplaylist"     : "True"}
        self.FFMPEG_OPTIONS = {"before_options" : "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options"        : "-vn",
                               "executable"     : config.FFMPEG_PATH}
        self.vc = "" # Stores the current channel

# ================================== FUNCTIONS =================================== #
    async def search_yt(self, item, ctx):
        """ Searches YouTube for the requested search term or URL, returns a
        URL and other info for the first result only."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)["entries"][0]
                ytdl_data = info
            except Exception as e:
                raise e
                print("====================================\n" + Style.RESET_ALL)
                return False
        print("====================================\n" + Style.RESET_ALL)

        member_obj = await ctx.guild.fetch_member(ctx.author.id)
        uname = f"{member_obj.name}#{member_obj.discriminator}"
        nick = member_obj.nick
        song_object = JukeBot.Track(ytdl_data, ctx)
        return song_object

        # return {"source"    : info["formats"][0]["url"],
        #         "title"     : info["title"],
        #         "thumb"     : info["thumbnails"][2]["url"],
        #         "duration"  : str(datetime.timedelta(seconds=info["duration"])),
        #         "web_url"   : info["webpage_url"],
        #         "requestor" : f"{nick} ({uname})"}

    async def play_audio(self, ctx, from_skip=False):
        """If the bot is not playing at all, this will play the first track in
        the queue, then immediately invoke play_next() afterwards."""
        if len(self.music_queue) > 0: # If there are tracks in the queue...
            # ...state that the bot is about to start playing...
            self.is_playing = True

            # ...get the first URL...
            media_url = self.music_queue[0].source

            # ...join a VC if not already in one...
            if self.vc == "":
                self.vc = await self.music_queue[0].voice_channel.connect()

            # ...then play the music in the current VC!
            # Once the music is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.vc.play(discord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            # ...state that the bot is no longer playing, stopping the play loop.
            self.is_playing = False

    def play_next(self, ctx):
        """Plays the next track in the queue. Different to play_audio() in that
        it does not attempt to join a VC. Doing so would make this async, which
        won't work with discord.py/nextcord's ability to invoke a lambda once
        audio is finished playing. It's tricky. Maybe TODO?"""

        # Remove the previously-played song from the queue to move to the next one.
        if self.music_queue != []:  # This'll throw an exception if we try to pop from an empty list...
            self.music_queue.pop(0) # ...so we do this otherwise-useless check to avoid clogging up logs.

        # If there are any more tracks waiting in the queue...
        if len(self.music_queue) > 0:
            self.is_playing = True
            media_url = self.music_queue[0].source
            self.vc.play(discord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

        else:
            self.is_playing = False

# =================================== COMMANDS =================================== #

    @commands.command(aliases=["p"])
    async def play(self, ctx, *args):
        """**Plays a song in the voice channel that you're currently in.**
        `<prefix>play` is the bread and butter of your JukeBot experience.
        Once you're in a voice channel, put the name of the song, or a YouTube
        link to the song, that you would like to play after the `<prefix>play`
        command, and it will begin playing in your voice channel.
        If there's music currently playing, the song is instead added to the
        queue.

        **Examples**
        `<prefix>play` takes 1 parameter. This can either be the URL to a
        YouTube video, or a seqrch query that you would type into Youtube to
        find that video (see examples).

        `<prefix>play `
        `<prefix>play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        `<prefix>play earth wind and fire september`

        **Aliases** — **<prefix>play** can also be invoked with:
        `<prefix>p`
        """
        search_query = " ".join(args)
        loading_msg = await ctx.send(f"`Loading track \"{search_query}\"...`")

        if ctx.author.voice is None:
            await ctx.send(embed=dialogBox("Warn", "Hang on!", "Connect to a voice channel first, _then_ issue the command."))
            return

        voice_channel = ctx.author.voice.channel # Set which voice channel to join later on in the command

        song_data = await self.search_yt(search_query, ctx) # Search YouTube for the video/query that the user requested.
        if song_data == False: # Comes back if the video is unable to be played due to uploader permissions, or if we got a malformed link.
            await ctx.send(embed=dialogBox("Error", "Unable to play song", "Incorrect video format or link type."))
            return
        song_data.voice_channel = voice_channel

        # Add the song data to JukeBot's queue.
        self.music_queue.append(song_data)
        # self.music_queue.append({
        #     "song_data"     : song_data,
        #     "voice_channel" : voice_channel
        # })

        await loading_msg.delete()
        # Start preparing the dialog to be posted.
        reply = dialogBox("Queued", f"Adding to queue: {song_data.title}", url=song_data.web_url)
        reply.set_thumbnail(url=song_data.thumb)
        reply.add_field(name="Duration" , value=song_data.duration, inline=True)
        reply.add_field(name="Requested by" , value=song_data.requestor, inline=True)

        await ctx.send(embed=reply)

        if self.is_playing == False:
            await self.play_audio(ctx)

    @commands.command()
    async def queue(self, ctx):
        """**Displays the queue of music waiting to be played.**
        The first track will be the one currently playing.

        **Examples**
        `<prefix>queue` takes no parameters.

        `<prefix>queue`
        """
        queue = "".join([f"{track+1} — {self.music_queue[track].title}\n" for track in range(0, len(self.music_queue))]) # God this sucks
        if self.vc == "":
            reply = embed=dialogBox("Warn", "Hang on!", "Connect to a voice channel first, _then_ issue the command.")
        else:
            reply = embed=dialogBox("Queued", "Queued music", f"`{queue}`")

        await ctx.send(embed=reply)

    @commands.command()
    async def skip(self, ctx):
        """**Skips the song currently playing.**
        If there are still tracks in the queue, the next one will automatically
        play, otherwisethe bot will stop playing.

        **Examples**
        `<prefix>skip` takes no parameters.

        `<prefix>skip`
        """
        if self.vc == "":
            reply = dialogBox("Warn", "Hang on!", "JukeBot is currently not playing; there's nothing to skip.")
        else:
            reply = dialogBox("Skip", "Skipped track")
            self.vc.stop() # Next track should automatically play (worked in testing, lets see how it goes...)

        await ctx.send(embed=reply)

    @commands.command()
    async def clear(self, ctx, *args):
        """**Removes all songs from the queue.**
        Does not affect the currently-playing song.

        **Examples**
        `<prefix>clear` takes either one or zero parameters. If a number is
        provided, the track in that position in the queue will be removed. If
        no parameters are provided, the entire queue will be cleared.

        `<prefix>clear`
        `<prefix>clear 3`
        """
        if self.music_queue == []:
            reply = dialogBox("Warn", "Hang on!", "The queue is already empty.")
            await ctx.send(embed=reply)
            return

        if args:
            track_to_remove = int(args[0])
            if track_to_remove:
                track_title = self.music_queue[track_to_remove - 1].title
                track_thumb = self.music_queue[track_to_remove - 1].thumb
                self.music_queue.pop(track_to_remove - 1)
                reply = dialogBox("Queued", f"Removed track no. {track_to_remove} from queue", track_title)
                reply.set_thumbnail(url=track_thumb)
                await ctx.send(embed=reply)
                return

        else:
            self.music_queue = []
            reply = dialogBox("Queued", "Cleared queue")
            await ctx.send(embed=reply)

    @commands.command(aliases=["np", "playing"])
    async def nowplaying(self, ctx):
        """te4st"""
        currently_playing = self.music_queue[0]
        reply = dialogBox("Playing", "Currently playing", currently_playing.title)
        reply.set_thumbnail(url=currently_playing.thumb)
        msg = await ctx.send(embed=reply)
