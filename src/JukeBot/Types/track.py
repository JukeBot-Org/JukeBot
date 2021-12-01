"""Defines how track data is stored."""
import datetime
from JukeBot.Utils.misc import humanize_duration


class Track:
    """Data structure for a track in the queue."""
    def __init__(self,
                 source: str,
                 title: str,
                 thumb: str,
                 web_url: str,
                 duration: int,
                 ctx):
        # Track data
        self.source = source  # The URL/file path to play with FFmpeg later on.
        self.title = title  # The title of the track
        self.thumb = thumb  # The YT thumbnail, Spotify cover art, id3 album art, etc.
        self.duration = datetime.timedelta(seconds=duration)
        self.web_url = web_url

        # Additional data for track
        self.human_duration = humanize_duration(self.duration.total_seconds())
        self.requestor = f"{ctx.author.name}#{ctx.author.discriminator}"  # TODO: reduce this down to just ctx.author
        self.requestor_uid = ctx.author.id
        self.voice_channel = ctx.author.voice.channel
        self.time_started = None  # Will eventually be set via arrow.utcnow() when track begins playing
        self.time_paused = None  # Will eventually be set via arrow.utcnow() when player is paused
        self.total_pause_time = 0  # Stores how long the track has been paused for.

    def __str__(self):
        return f"\"{self.title}\" ({self.duration}), requested by {self.requestor}"

    def time_left(self, time_now):
        diff = (time_now - self.time_started).total_seconds() - self.total_pause_time

        time_left = humanize_duration(self.duration.total_seconds() - diff)
        return time_left
