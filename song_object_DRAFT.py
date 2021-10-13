"""A future implementation of a class for songs, rather than storing them as
dict items. Not yet implemented. Kept here purely as a whiteboard/scratch-pad.
"""
import datetime

class Track:
    """Represents a track in the queue."""
    def __init__(self, ytdl_data, ctx):
        # Info about the user requesting this track.
        member_obj = ctx.guild.get_member(ctx.author.id)
        uname = f"{member_obj.name}#{member_obj.discriminator}"
        nick = member_obj.nick

        # Track data
        self.source    = ytdl_data["formats"][0]["url"],
        self.title     = ytdl_data["title"],
        self.thumb     = ytdl_data["thumbnails"][2]["url"],
        self.duration  = str(datetime.timedelta(seconds=ytdl_data["duration"])),
        self.web_url   = ytdl_data["webpage_url"],
        self.requestor = f"{nick} ({uname})"}

class Queue:
    def __init__(self):
        self.foo = "bar"
