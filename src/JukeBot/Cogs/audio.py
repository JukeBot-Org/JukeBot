import nextcord
from nextcord import FFmpegPCMAudio
from nextcord.ext import commands
from nextcord.ext import tasks
import arrow
import logging
import JukeBot
from JukeBot.Utils.embed_dialogs import dialogBox
import JukeBot.Messages as msgs
import asyncio


class Audio(commands.Cog):
    """Handles all of the audio-playing commands and operations."""
    def __init__(self, client):
        self.client = client

        # Stores JukeBot.Queue objects for each guild.
        self.all_queues = {}

        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn",
                               "executable": JukeBot.Config.FFMPEG_PATH}
        # After idling for this amount of time in seconds, JukeBot will disconnect from the voice channel.
        self.time_to_idle_for = JukeBot.Config.MAX_IDLE_TIME

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
            if self.all_queues[q].current_idle_time > JukeBot.Config.MAX_IDLE_TIME:
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

    async def play_audio(self, ctx, cont=False):
        """If the bot is not playing at all when !play is invoked, this will
        play the first track in the queue, then immediately invoke play_next()
        afterwards."""
        guild_queue = self.all_queues[ctx.guild.id]

        # If we just finished playing another track, remove it from the queue.
        if self.all_queues[ctx.guild.id].is_empty() is False and cont is True:
            self.all_queues[ctx.guild.id].remove_track(0)

        if len(guild_queue.tracks) > 0:  # If there are tracks in the queue...
            # ...state that the bot is about to start playing...
            guild_queue.is_playing = True

            logging.info(f"Playing {guild_queue.tracks[0]}")

            # ...get the first URL...
            media_url = guild_queue.tracks[0].source

            # ...join a VC if not already in one...
            if guild_queue.audio_player is None:
                guild_queue.audio_player = await guild_queue.tracks[0].voice_channel.connect()

            # ...record when the track started playing...
            guild_queue.tracks[0].time_started = arrow.utcnow()

            # ...then play the track in the current VC!
            # Once the track is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            print(media_url)
            guild_queue.audio_player.play(FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS),
                                          after=lambda e: asyncio.run(self.play_audio(ctx, cont=True)))
        else:
            # ...state that the bot is no longer playing, stopping the play loop.
            guild_queue.is_playing = False

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
        # Take in the user's query and try to find the track(s) for them.
        loading_msg = await ctx.send(f"`Loading \"{search_query}\"...`")
        requested_tracks, playlist_info = await JukeBot.TrackSearch.find(search_query, ctx, loading_msg)
        print(f"type(requested_tracks) = {type(requested_tracks)}")
        print(f"type(playlist_info) = {type(playlist_info)}")

        # No tracks returned. Occurs if there was any kind of exception
        # when executing JukeBot.TrackSearch.find()
        if len(requested_tracks) <= 0:
            reply = dialogBox("Error", "Unable to play track",
                              msgs.CANNOT_PLAY)
            reply.set_footer(text=msgs.EPHEMERAL_FOOTER)
            await ctx.send(embed=reply, delete_after=10)
            await loading_msg.delete()
            return

        # A single track returned. Either a YouTube or Spotify track.
        elif len(requested_tracks) == 1:
            track_data = requested_tracks[0]
            # Add the track data to JukeBot's queue for this guild.
            self.all_queues[ctx.guild.id].add_track(track_data)

            # Start preparing the dialog to be posted.
            reply = dialogBox("Queued",
                              f"Adding to queue: {track_data.title}",
                              url=track_data.web_url)
            reply.set_thumbnail(url=track_data.thumb)
            reply.add_field(name="Duration",
                            value=track_data.human_duration,
                            inline=True)

        # Multiple tracks returned. Most likely a Spotify album or playlist.
        elif len(requested_tracks) >= 2:
            tracks_for_embed = []
            reply = dialogBox("Queued",
                              f"Added tracks from the {playlist_info['type']} \"{playlist_info['name']}\" to the queue")
            reply.set_thumbnail(url=playlist_info["thumb"])
            for track_data in requested_tracks:
                tracks_for_embed.append(f"• {track_data.title}")
                # Add the track data to JukeBot's queue for this guild.
                self.all_queues[ctx.guild.id].add_track(track_data)
            if len(tracks_for_embed) > 3:
                x = tracks_for_embed[:3]
                x.append(f"...and {len(tracks_for_embed)-len(x)} more.")
                tracks_for_embed = x
            reply.add_field(name="Tracks added",
                            value="```" + "".join(f"{x}\n" for x in tracks_for_embed) + "```",
                            inline=False)

        # Finish off the reply embed...
        reply.add_field(name="Requested by",
                        value=track_data.requestor,
                        inline=True)

        # Delete the loading message, send the success message.
        await loading_msg.delete()
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
