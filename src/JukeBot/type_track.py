"""Defines how track data is stored."""
import datetime
from JukeBot.utils.misc import humanize_duration


class Track:
    """Represents a track in the queue."""
    def __init__(self, ytdl_data, ctx):
        # Track data from YouTube
        self.source = ytdl_data["formats"][0]["url"]
        self.title = ytdl_data["title"]
        self.thumb = ytdl_data["thumbnails"][2]["url"]
        self.duration = datetime.timedelta(seconds=ytdl_data["duration"])
        self.web_url = ytdl_data["webpage_url"]

        # Additional data for track
        self.human_duration = humanize_duration(self.duration.total_seconds())
        self.requestor = f"{ctx.author.name}#{ctx.author.discriminator}"
        self.requestor_uid = ctx.author.id
        self.voice_channel = None  # Will be set later on in audio_commands.search_yt()
        self.time_started = None  # Will eventually be set via arrow.utcnow() when track begins playing
        self.time_paused = None  # Will eventually be set via arrow.utcnow() when player is paused
        self.total_pause_time = 0  # Stores how long the track has been paused for.

    def __str__(self):
        return f"\"{self.title}\" ({self.duration}), requested by {self.requestor} [{self.web_url}]"

    def time_left(self, time_now):
        diff = (time_now - self.time_started).total_seconds() - self.total_pause_time

        time_left = humanize_duration(self.duration.total_seconds() - diff)
        return time_left
