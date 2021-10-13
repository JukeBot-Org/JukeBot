import datetime
import arrow

def humanize_duration(total_seconds):
    hours, remainder = divmod(int(total_seconds),60*60)
    minutes, seconds = divmod(remainder,60)
    final_representation = (f"{hours} hr " if hours>0 else "") + (f"{minutes} min " if minutes>0 else "") + f"{seconds} sec "
    return final_representation

class Track:
    """Represents a track in the queue."""
    def __init__(self, ytdl_data, ctx):
        # Track data
        self.source         = ytdl_data["formats"][0]["url"]
        self.title          = ytdl_data["title"]
        self.thumb          = ytdl_data["thumbnails"][2]["url"]
        self.duration       = datetime.timedelta(seconds=ytdl_data["duration"])
        self.human_duration = humanize_duration(self.duration.total_seconds())
        self.web_url        = ytdl_data["webpage_url"]
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
