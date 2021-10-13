import datetime

class Track:
    """Represents a track in the queue."""
    def __init__(self, ytdl_data, ctx):
        # Track data
        self.source        = ytdl_data["formats"][0]["url"]
        self.title         = ytdl_data["title"]
        self.thumb         = ytdl_data["thumbnails"][2]["url"]
        self.duration      = str(datetime.timedelta(seconds=ytdl_data["duration"]))
        self.web_url       = ytdl_data["webpage_url"]
        self.requestor     = f"{ctx.author.name}#{ctx.author.discriminator}"
        self.voice_channel = None # Will be set later on in music_commands.search_yt()
    def __str__(self):
        return f"{self.title} ({self.duration}), requested by {self.requestor}"
