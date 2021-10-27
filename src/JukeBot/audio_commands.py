import nextcord
from nextcord.ext import commands, tasks
from youtube_dl import YoutubeDL
from colorama import Fore, Style
import datetime
import arrow
import logging
import asyncio

import time
import json

import JukeBot.config
from JukeBot.embed_dialogs import dialogBox
import JukeBot.queue
import JukeBot.track
from JukeBot.track import humanize_duration
import JukeBot.checks


class Audio(commands.Cog):
    """The cog that handles all of the audio-playing commands and operations."""
    def __init__(self, client):
        self.client = client

        # Determines whether or not the bot is currently playing.
        # If audio is already playing and a new play request is received, it will instead be queued.
        self.is_playing = False

        self.queue = JukeBot.queue.Queue()
        self.YDL_OPTIONS = {"format": "bestaudio",
                            "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn",
                               "executable": JukeBot.config.FFMPEG_PATH}
        self.voice_channel = None  # Stores the current channel
        self.idled_time = 0
        self.time_to_idle_for = JukeBot.config.MAX_IDLE_TIME
        self.last_text_channel = None  # nextcord.TextChannel object

# ================================== FUNCTIONS =================================== #

    @tasks.loop(seconds=1.0, count=None)
    async def idle_timer(self):
        """This task is started when JukeBot begins playing audio, triggering
        every second. When the queue is exhausted and is_playing is False, the
        idled_time counter will increment every second. Once the idle_time
        counter == the amount in self.time_to_idle_for, JukeBot will disconnect
        from its current voice channel and send a message to the channel in
        which the most recent command was issued.
        """
        if not self.is_playing:
            self.idled_time += 1
            print(f"Idled for {self.idled_time} seconds")
            if self.idled_time >= self.time_to_idle_for:
                logging.info(f"Idled for {self.idled_time} seconds")
                await self.voice_channel.disconnect()
                reply = dialogBox("Eject", "JukeBot has auto-DC'd from the voice channel.",
                                  f"In order to save bandwidth and keep things tidy, JukeBot automatically disconnects after {humanize_duration(self.time_to_idle_for)} of inactivity.\nHit `{JukeBot.config.COMMAND_PREFIX}play` to start JukeBot again.")
                reply.set_thumbnail(url="https://cdn.discordapp.com/avatars/886200359054344193/4da9c1e1257116f08c99c904373b47b7.png")
                reply.set_footer(text="This message will automatically disappear shortly.")
                await self.last_text_channel.send(embed=reply, delete_after=120)
        if self.is_playing:
            self.idled_time = 0

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Fires when JukeBot changes voice channels. If disconnecting from a
        voice channel, reset the queue and start the idle timer, after which
        the bot will disconnect.
        TODO: implement a total play-time tracker.
        """
        if member is not member.guild.me:
            return  # Make sure we only fire the below for JukeBot, not anybody else.

        if before.channel is None and after.channel is not None:
            logging.info(f"Connected to voice channel \"{after.channel}\"")

        elif before.channel is not None and after.channel is None:
            logging.info(f"Disconnecting from voice channel \"{before.channel}\"")
            # If the bot was manually disconnected, we need to clean up the broken voice client connection.
            # NOTE: I've submitted a bugfix pull request to Nextcord which, when marged into the main repo,
            # will make the four lines below redundant.
            voice_client = nextcord.utils.get(self.client.voice_clients, guild=self.last_text_channel.guild)
            if voice_client:
                await voice_client.disconnect()
                voice_client.cleanup()

            # Reset a few vars
            self.voice_channel = None
            self.queue.clear()
            self.is_playing = False

            # Stop the idle timer if it's running.
            self.idle_timer.stop()
            logging.info(f"Successfully disconnected from voice channel \"{before.channel}\"")

    async def search_yt(self, item, ctx):
        """Searches YouTube for the requested search term or URL, returns a
        JukeBot.track.Track object for the first result only."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)["entries"][0]
                ytdl_data = info
            except Exception as e:
                print("====================================\n" + Style.RESET_ALL)
                raise e
                return False
        print("====================================\n" + Style.RESET_ALL)

        track_obj = JukeBot.track.Track(ytdl_data, ctx)
        return track_obj

    async def play_audio(self, ctx, from_skip=False):
        """If the bot is not playing at all, this will play the first track in
        the queue, then immediately invoke play_next() afterwards."""
        if len(self.queue.tracks) > 0:  # If there are tracks in the queue...
            # ...state that the bot is about to start playing...
            self.is_playing = True

            logging.info(f"Playing {self.queue.tracks[0]}")

            # ...get the first URL...
            media_url = self.queue.tracks[0].source

            # ...join a VC if not already in one...
            if self.voice_channel is None:
                self.voice_channel = await self.queue.tracks[0].voice_channel.connect()
                self.idle_timer.start()

            # ...record when the track started playing...
            self.queue.tracks[0].time_started = arrow.utcnow()

            # ...then play the track in the current VC!
            # Once the track is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.voice_channel.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            # ...state that the bot is no longer playing, stopping the play loop.
            self.is_playing = False

    def play_next(self, ctx):
        """Plays the next track in the queue. Different to play_audio() in that
        it does not attempt to join a VC. Doing so would make this async, which
        won't work with nextcord's ability to invoke a lambda once audio is
        finished playing audio. It's tricky. Maybe TODO?"""

        # Remove the previously-played track from the queue to move to the next one.
        if self.queue.is_empty() is False:  # This'll throw an exception if we try to pop from an empty list...
            self.queue.remove_track(0)      # ...so we do this otherwise-useless check to avoid clogging up logfiles.

        # If there are any more tracks waiting in the queue...
        if len(self.queue.tracks) > 0:
            self.is_playing = True

            media_url = self.queue.tracks[0].source
            self.queue.tracks[0].time_started = arrow.utcnow()
            self.voice_channel.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

        else:
            self.is_playing = False

# =================================== COMMANDS =================================== #

    @commands.command(name="play", aliases=["p"])
    @JukeBot.checks.user_in_vc()
    async def _play(self, ctx, *params):
        """**Plays a track in the voice channel that you're currently in.**
        Once you're in a voice channel, put the name of the track, or a YouTube
        link to the track, that you would like to play after the `<prefix>play`
        command, and it will begin playing in your voice channel.
        If there's a track currently playing, the track is instead added to the
        queue.

        **Examples**
        `<prefix>play` takes 1 parameter. This can either be the URL to a
        YouTube video, or a search query that you would type into Youtube to
        find that video (see examples).

        `<prefix>play `
        `<prefix>play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        `<prefix>play earth wind and fire september`

        **Aliases** — Instead of **<prefix>play**, you can also use:
        `<prefix>p`
        """
        search_query = " ".join(params)
        self.last_text_channel = ctx.channel
        loading_msg = await ctx.reply(f"`Loading track \"{search_query}\"...`")

        track_data = await self.search_yt(search_query, ctx)  # Search YouTube for the video/query that the user requested.
        if track_data is False:  # Comes back if the video is unable to be played due to uploader permissions, or if we got a malformed link.
            reply = dialogBox("Error", "Unable to play track", "Incorrect video format or link type.")
            reply.set_footer(text="This message will automatically disappear shortly.")
            await ctx.reply(embed=reply, delete_after=10)
            return
        track_data.voice_channel = ctx.author.voice.channel

        # Add the track data to JukeBot's queue.
        self.queue.add_track(track_data)

        # Start preparing the dialog to be posted.
        await loading_msg.delete()
        reply = dialogBox("Queued", f"Adding to queue: {track_data.title}", url=track_data.web_url)
        reply.set_thumbnail(url=track_data.thumb)
        reply.add_field(name="Duration", value=track_data.human_duration, inline=True)
        reply.add_field(name="Requested by", value=track_data.requestor, inline=True)

        await ctx.reply(embed=reply)

        if self.is_playing is False:
            await self.play_audio(ctx)

    @commands.command(name="queue")
    @JukeBot.checks.jukebot_in_vc()
    async def _queue(self, ctx):
        """**Displays the queue of tracks waiting to be played.**
        The first track will be the one currently playing.

        **Examples**
        `<prefix>queue` takes no parameters.

        `<prefix>queue`
        """
        reply = dialogBox("Queued", "Queued tracks", self.queue.pretty_display())
        await ctx.reply(embed=reply)

    @commands.command(name="skip")
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.is_playing()
    async def _skip(self, ctx):
        """**Skips the track currently playing.**
        If there are still tracks in the queue, the next one will automatically
        play, otherwisethe bot will stop playing.

        **Examples**
        `<prefix>skip` takes no parameters.

        `<prefix>skip`
        """

        reply = dialogBox("Skip", "Skipped track")
        self.voice_channel.stop()  # Next track should automatically play (worked in testing, lets see how it goes...)

        reply.set_footer(text="This message will automatically disappear shortly.")
        await ctx.reply(embed=reply, delete_after=10)

    # TODO: check if the track exists in the queue before invoking
    @commands.command(name="clear")
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.queue_not_empty()
    async def _clear(self, ctx, *params):
        """**Removes all tracks from the queue.**
        Does not affect the currently-playing track. `<prefix>clear` can be
        followed by the number of an item in the queue to remove only that
        track rather then all of them.
        This is useful when you want JukeBot to stop, but once the current
        track is finished (or when someone fills the queue with nonsense and
        you want to start from scratch while not interrupting the music).

        **Examples**
        `<prefix>clear` takes either one or zero parameters. If a number is
        provided, the track in that position in the queue will be removed. If
        no parameters are provided, the entire queue will be cleared.

        `<prefix>clear`
        `<prefix>clear 3`
        """

        if params:
            track_to_remove = int(params[0])
            if track_to_remove:
                track_title = self.queue.tracks[track_to_remove - 1].title
                track_thumb = self.queue.tracks[track_to_remove - 1].thumb
                self.queue.remove_track(track_to_remove - 1)
                reply = dialogBox("Queued", f"Removed track no. {track_to_remove} from queue", track_title)
                reply.set_thumbnail(url=track_thumb)
                reply.set_footer(text="This message will automatically disappear shortly.")
                await ctx.reply(embed=reply, delete_after=10)
                return

        else:
            self.queue.clear()
            reply = dialogBox("Queued", "Cleared queue")
            reply.set_footer(text="This message will automatically disappear shortly.")
            await ctx.reply(embed=reply, delete_after=10)

    @commands.command(name="nowplaying", aliases=["np", "playing"])
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.is_playing()
    @JukeBot.checks.queue_not_empty()
    async def _nowplaying(self, ctx):
        """**Displays the currently-playing track.**
        Includes the amount of time left in the track as well..

        **Examples**
        `<prefix>nowplaying` takes no parameters.

        `<prefix>nowplaying`

        **Aliases** — Instead of **<prefix>nowplaying**, you can also use:
        `<prefix>np`
        `<prefix>playing`
        """
        currently_playing = self.queue.tracks[0]
        reply = dialogBox("Playing", "Currently playing", currently_playing.title, url=currently_playing.web_url)
        reply.set_thumbnail(url=currently_playing.thumb)
        reply.add_field(name="Duration", value=currently_playing.human_duration, inline=True)
        reply.add_field(name="Time remaining", value=currently_playing.time_left(arrow.utcnow()), inline=True)
        msg = await ctx.reply(embed=reply)

    @commands.command(name="stop", aliases=["leave", "disconnect"])
    @JukeBot.checks.jukebot_in_vc()
    async def _stop(self, ctx):
        """**Halts JukeBox entirely.**
        Stops JukeBot playing audio, clears the queue, and disconnects it
        from the current voice channel. JukeBot will remain disconnected until
        a user starts it again with `<prefix>play`.

        **Examples**
        `<prefix>stop` takes no parameters.

        `<prefix>stop`

        **Aliases** — Instead of **<prefix>stop**, you can also use:
        `<prefix>leave`
        `<prefix>disconnect`
        """
        self.voice_channel.stop()
        self.queue.clear()
        self.voice_channel.disconnect()

        reply = dialogBox("Eject", "JukeBot stopped", "Music stopped and queue cleared.")
        reply.set_footer(text="This message will automatically disappear shortly.")
        await ctx.reply(embed=reply, delete_after=10)

    @commands.command(name="pause")
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.is_playing()
    @JukeBot.checks.not_paused()
    async def _pause(self, ctx):
        """**Pauses playback.**
        Music will remain paused until the track is resumed with `<prefix>resume`.

        **Examples**
        `<prefix>pause` takes no parameters.

        `<prefix>pause`
        """
        # Store the current clock time.
        # Later on, this will be referenced when we need to see how many
        # seconds the track has been paused for.
        self.queue.tracks[0].time_paused = arrow.utcnow()

        # Pause the player
        self.voice_channel.pause()
        self.queue.is_paused = True

        reply = dialogBox("Paused", "Paused track", f"Type `{JukeBot.config.COMMAND_PREFIX}resume` to resume the track.")
        reply.set_footer(text="This message will automatically disappear shortly.")
        await ctx.reply(embed=reply, delete_after=10)

    @commands.command(name="resume", aliases=["unpause"])
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.is_playing()
    @JukeBot.checks.is_paused()
    async def _resume(self, ctx):
        """**Resumes playback of a paused track.**
        A track must be currently paused for this command to work.

        **Examples**
        `<prefix>resume` takes no parameters.

        `<prefix>resume`

        **Aliases** — Instead of **<prefix>resume**, you can also use:
        `<prefix>unpause`
        """

        # Calculate how long the track has been paused for.
        time_paused = self.queue.tracks[0].time_paused
        total_pause_time = (arrow.utcnow() - time_paused).total_seconds()
        self.queue.tracks[0].total_pause_time += total_pause_time

        # Resume the player
        self.voice_channel.resume()
        self.queue.is_paused = False
        reply = dialogBox("Playing", f"Resumed track: **{self.queue.tracks[0].title}**")
        reply.set_footer(text="This message will automatically disappear shortly.")
        await ctx.reply(embed=reply, delete_after=10)

    @commands.command(name="tq", hidden=True)
    @JukeBot.checks.user_in_vc()
    @JukeBot.checks.is_developer()
    async def _tq(self, ctx):
        """**Internal command.**
        Loads some example tracks for testing queue-related operations.
        """
        await ctx.reply(embed=dialogBox("Debug", "Loading test queue..."))
        await ctx.invoke(self.client.get_command('play'), 'one')
        await ctx.invoke(self.client.get_command('play'), 'two')
        await ctx.invoke(self.client.get_command('play'), 'three')
        # await ctx.invoke(self.client.get_command('play'), 'four')
        # await ctx.invoke(self.client.get_command('play'), 'five')
        # await ctx.invoke(self.client.get_command('play'), 'six')
        await ctx.invoke(self.client.get_command('queue'))
        await ctx.reply(embed=dialogBox("Debug", "Test queue finished loading."))

    @commands.command(name="chunt")
    async def _foo(self, ctx):
        await ctx.reply("in command")
