import nextcord
from nextcord.ext import commands
from nextcord.ext import tasks
import youtube_dl
from colorama import Fore, Style
import arrow
import logging
import JukeBot
from JukeBot.utils.embed_dialogs import dialogBox
import JukeBot.messages as msgs


class Audio(commands.Cog):
    """Handles all of the audio-playing commands and operations."""
    def __init__(self, client):
        self.client = client

        # Stores JukeBot.Queue objects for each guild.
        self.all_queues = {}

        self.YDL_OPTIONS = {"format": "bestaudio",
                            "noplaylist": "True"}
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn",
                               "executable": JukeBot.config.FFMPEG_PATH}
        # After idling for this amount of time in seconds, JukeBot will disconnect from the voice channel.
        self.time_to_idle_for = JukeBot.config.MAX_IDLE_TIME

        # Gets the VC of the guild we're currently in.
        self.current_guild_vc = lambda g: nextcord.utils.get(self.client.voice_clients, guild=g)

        # Initialise guild queues for each guild that this instance of JukeBot is currently in.
        for g in self.client.guilds:
            self.all_queues[g.id] = JukeBot.Queue(g)

        # Start tracking how long each guild instance has been idling for.
        # This doesn't look like it scales well. Uhh, TODO?
        self.idle_timer.start()

# ================================ FUNCTIONS ================================ #

    @tasks.loop(seconds=1.0, count=None)
    async def idle_timer(self):
        """This loop runs for as long as JukeBot is online. It checks every
        second to see if any guild instances of JukeBot are not playing and
        are still connected to the voice channel. If so, it waits an amount
        of seconds equal to MAX_IDLE_TIME, after which the bot disconnects.
        """
        for q in self.all_queues:
            if self.all_queues[q].is_playing is not False:
                continue  # Skip any bot instances that are currently playing audio.
            if self.all_queues[q].audio_player is None:
                continue  # A guild with no audio player has already DC'd.

            self.all_queues[q].current_idle_time += 1
            if self.all_queues[q].current_idle_time > JukeBot.config.MAX_IDLE_TIME:
                await self.all_queues[q].audio_player.disconnect()
                self.all_queues[q].current_idle_time = 0

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Fires when JukeBot changes voice channels. If disconnecting from a
        voice channel, it clears the guild's queue and stops the guild's idle
        timer.
        TODO: implement a total play-time tracker.
        """
        if member is not member.guild.me:
            return  # Make sure we only fire the below for JukeBot, not anybody else.

        if before.channel is None and after.channel is not None:
            logging.info(f"Connected to voice channel \"{after.channel}\"")

        elif before.channel is not None and after.channel is None:
            logging.info(f"Attempting to disconnect from voice channel \"{before.channel}\"...")
            # If the bot was manually disconnected, we need to clean up the
            # broken voice client connection.
            # NOTE: I've submitted a bugfix pull request to Nextcord which, in
            # the next main release, will make the four lines below redundant.
            voice_client = self.current_guild_vc(member.guild)
            if voice_client:
                await voice_client.disconnect()
                voice_client.cleanup()

            # Reset a few vars
            self.all_queues[member.guild.id].audio_player = None
            self.all_queues[member.guild.id].clear()
            self.all_queues[member.guild.id].is_playing = False
            logging.info(f"Successfully disconnected from voice channel \"{before.channel}\"")

    async def search_yt(self, item, ctx):
        """Searches YouTube for the requested search term or URL, returns a
        JukeBot.Track object for the first result only."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:  # If we get a DownloadError while trying to fetch the YouTube data, it's probably a stream.
                ydl_results = ydl.extract_info(f"ytsearch:{item}", download=False)["entries"]
            except Exception as e:
                print(type(e))
                return False
            if len(ydl_results) == 0:  # The list above will be empty if there were any issues.
                return False
            ytdl_data = ydl_results[0]
        print("====================================\n" + Style.RESET_ALL)

        track_obj = JukeBot.Track(ytdl_data, ctx)
        return track_obj

    async def play_audio(self, ctx):
        """If the bot is not playing at all when !play is invoked, this will
        play the first track in the queue, then immediately invoke play_next()
        afterwards."""
        if len(self.all_queues[ctx.guild.id].tracks) > 0:  # If there are tracks in the queue...
            # ...state that the bot is about to start playing...
            self.all_queues[ctx.guild.id].is_playing = True

            logging.info(f"Playing {self.all_queues[ctx.guild.id].tracks[0]}")

            # ...get the first URL...
            media_url = self.all_queues[ctx.guild.id].tracks[0].source

            # ...join a VC if not already in one...
            if self.all_queues[ctx.guild.id].audio_player is None:
                self.all_queues[ctx.guild.id].audio_player = await self.all_queues[ctx.guild.id].tracks[0].voice_channel.connect()

            # ...record when the track started playing...
            self.all_queues[ctx.guild.id].tracks[0].time_started = arrow.utcnow()

            # ...then play the track in the current VC!
            # Once the track is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.all_queues[ctx.guild.id].audio_player.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            # ...state that the bot is no longer playing, stopping the play loop.
            self.all_queues[ctx.guild.id].is_playing = False

    def play_next(self, ctx):
        """Plays the next track in the queue. Different to play_audio() in thatNO
        it does not attempt to join a VC. Doing so would make this
        asynchronous, which won't work with nextcord's ability to invoke a
        lambda once audio is finished playing audio. It's tricky. Maybe TODO?"""
        # Remove the previously-played track from the queue to move to the next one.
        if self.all_queues[ctx.guild.id].is_empty() is False:  # This'll throw an exception if we try to pop from an empty list...
            self.all_queues[ctx.guild.id].remove_track(0)      # ...so we do this otherwise-useless check to avoid clogging up logfiles.

        # If there are any more tracks waiting in the queue...
        if len(self.all_queues[ctx.guild.id].tracks) > 0:
            self.all_queues[ctx.guild.id].is_playing = True

            media_url = self.all_queues[ctx.guild.id].tracks[0].source
            self.all_queues[ctx.guild.id].tracks[0].time_started = arrow.utcnow()
            self.all_queues[ctx.guild.id].audio_player.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))

        # Otherwise, if the queue is exhausted...
        else:
            self.all_queues[ctx.guild.id].is_playing = False

# ================================ COMMANDS ================================= #

    @commands.command(name="play", aliases=["p"])
    @JukeBot.checks.user_in_vc()
    async def _play(self, ctx, *, search_query):
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

        `<prefix>play`
        `<prefix>play https://www.youtube.com/watch?v=dQw4w9WgXcQ`
        `<prefix>play earth wind and fire september`

        **Aliases** — Instead of **<prefix>play**, you can also use:
        `<prefix>p`
        """
        loading_msg = await ctx.send(f"`Loading track \"{search_query}\"...`")

        # Search YouTube for the video/query that the user requested.
        track_data = await self.search_yt(search_query, ctx)

        # Comes back False if the video is unable to be played due to uploader
        # permissions, or if we got a malformed link.
        if track_data is False:
            reply = dialogBox("Error", "Unable to play track",
                              msgs.CANNOT_PLAY)
            reply.set_footer(text=msgs.EPHEMERAL_FOOTER)
            await ctx.send(embed=reply, delete_after=10)
            return
        track_data.voice_channel = ctx.author.voice.channel

        # Add the track data to JukeBot's queue for this guild.
        self.all_queues[ctx.guild.id].add_track(track_data)

        # Start preparing the dialog to be posted.
        await loading_msg.delete()
        reply = dialogBox("Queued",
                          f"Adding to queue: {track_data.title}",
                          url=track_data.web_url)
        reply.set_thumbnail(url=track_data.thumb)
        reply.add_field(name="Duration",
                        value=track_data.human_duration,
                        inline=True)
        reply.add_field(name="Requested by",
                        value=track_data.requestor,
                        inline=True)

        await ctx.send(embed=reply)

        if self.all_queues[ctx.guild.id].is_playing is False:
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
        reply = dialogBox("Queued", "Queued tracks",
                          self.all_queues[ctx.guild.id].pretty_display())
        await ctx.send(embed=reply)

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

        # Next track should automatically play (worked in testing, lets see
        # how it goes...)
        self.all_queues[ctx.guild.id].audio_player.stop()
        await ctx.send(embed=reply)

    # TODO: check if the track exists in the queue before invoking
    @commands.command(name="clear")
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.queue_not_empty()
    async def _clear(self, ctx, *track_to_remove):
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
        if track_to_remove:
            track_to_remove = int(track_to_remove[0])
            if track_to_remove:
                track_title = self.all_queues[ctx.guild.id].tracks[track_to_remove - 1].title
                track_thumb = self.all_queues[ctx.guild.id].tracks[track_to_remove - 1].thumb
                self.all_queues[ctx.guild.id].remove_track(track_to_remove - 1)
                reply = dialogBox("Queued", f"Removed track no. {track_to_remove} from queue", track_title)
                reply.set_thumbnail(url=track_thumb)
                reply.set_footer(text=msgs.EPHEMERAL_FOOTER)
                await ctx.send(embed=reply, delete_after=10)
                return
        else:
            self.all_queues[ctx.guild.id].clear()
            reply = dialogBox("Queued", "Cleared queue")
            await ctx.send(embed=reply)

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
        currently_playing = self.all_queues[ctx.guild.id].tracks[0]
        reply = dialogBox("Playing", "Currently playing",
                          currently_playing.title,
                          url=currently_playing.web_url)
        reply.set_thumbnail(url=currently_playing.thumb)
        reply.add_field(name="Duration",
                        value=currently_playing.human_duration,
                        inline=True)
        reply.add_field(name="Time remaining",
                        value=currently_playing.time_left(arrow.utcnow()),
                        inline=True)
        await ctx.send(embed=reply)

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
        self.all_queues[ctx.guild.id].audio_player.stop()
        self.all_queues[ctx.guild.id].clear()
        await self.all_queues[ctx.guild.id].audio_player.disconnect()

        reply = dialogBox("Eject", "JukeBot stopped",
                          "Music stopped and queue cleared.")
        await ctx.send(embed=reply)

    @commands.command(name="pause")
    @JukeBot.checks.jukebot_in_vc()
    @JukeBot.checks.is_playing()
    @JukeBot.checks.is_not_paused()
    async def _pause(self, ctx):
        """**Pauses playback.**
        Music will remain paused until the track is resumed
        with `<prefix>resume`.

        **Examples**
        `<prefix>pause` takes no parameters.

        `<prefix>pause`
        """
        # Store the current clock time.
        # Later on, this will be referenced when we need to see how many
        # seconds the track has been paused for.
        self.all_queues[ctx.guild.id].tracks[0].time_paused = arrow.utcnow()

        # Pause the player
        self.all_queues[ctx.guild.id].audio_player.pause()

        reply = dialogBox("Paused", "Paused track",
                          f"{msgs.PLS_RESUME}")
        await ctx.send(embed=reply)

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
        time_paused = self.all_queues[ctx.guild.id].tracks[0].time_paused
        total_pause_time = (arrow.utcnow() - time_paused).total_seconds()
        self.all_queues[ctx.guild.id].tracks[0].total_pause_time += total_pause_time

        # Resume the player
        self.all_queues[ctx.guild.id].audio_player.resume()
        reply = dialogBox("Playing", f"Resumed track: **{self.all_queues[ctx.guild.id].tracks[0].title}**")
        await ctx.send(embed=reply)
