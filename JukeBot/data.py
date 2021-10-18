"""Defines how track and queue data is stored."""
import datetime

def humanize_duration(total_seconds):
    hours, remainder = divmod(int(total_seconds),60*60)
    minutes, seconds = divmod(remainder,60)
    final_representation = (f"{hours} hr " if hours>0 else "") + (f"{minutes} min " if minutes>0 else "") + f"{seconds} sec "
    return final_representation

class Track:
    """Represents a track in the queue."""
    def __init__(self, ytdl_data, ctx):
        # Track data from YouTube
        self.source         = ytdl_data["formats"][0]["url"]
        self.title          = ytdl_data["title"]
        self.thumb          = ytdl_data["thumbnails"][2]["url"]
        self.duration       = datetime.timedelta(seconds=ytdl_data["duration"])
        self.web_url        = ytdl_data["webpage_url"]

        # Additional data for track
        self.human_duration = humanize_duration(self.duration.total_seconds())
        self.requestor      = f"{ctx.author.name}#{ctx.author.discriminator}"
        self.requestor_uid  = ctx.author.id
        self.voice_channel  = None # Will be set later on in audio_commands.search_yt()
        self.time_started   = None # Will eventually be set via arrow.utcnow()

    def __str__(self):
        return f"\"{self.title}\" ({self.duration}), requested by {self.requestor} [{self.web_url}]"

    def time_left(self, time_now):
        diff = time_now - self.time_started
        time_left = humanize_duration(self.duration.total_seconds() - diff.total_seconds())
        return time_left

class Queue:
    """Represents the queue that JukeBot.Track objects are stored in.
    Currently doesn't do much more than consolidate a list and list.pop() into
    a single list, but leaves room for expansion.
    """
    def __init__(self):
        self.tracks = []

    def clear(self):
        self.tracks = []

    def remove_track(self, track_index_to_remove):
        self.tracks.pop(track_index_to_remove)

    def total_time():
        return None # Will eventually add up the total duration of all tracks in the queue.
