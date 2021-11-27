from JukeBot.utils.misc import trim
import nextcord
import JukeBot.messages as msgs


class Queue:
    """A Queue object is more than a queue of tracks. It stores information
    for each guild that this instance of JukeBot is running in. The Queue for
    a guild stores the VoiceClient object for that guild, tracks idle time,
    and more.
    """
    def __init__(self, guild: nextcord.Guild):
        # Stores an ordered list of the tracks in the queue.
        # 0th is playing currently, 1st is next, and so on.
        self.tracks = []

        # lmfao
        self.is_empty = lambda: not bool(self.tracks)

        # Tracks if the bot is playing. Need to remove this in favour of the
        # built-in nextcord equivalent (nextcord.VoiceChannel.is_playing).
        self.is_playing = False

        # A nextcord.VoiceChannel object representing the VC we're
        # in currently.
        self.audio_player = None

        # A nextcord.Guild object that contains info about the guild which
        # this queue is for.
        self.guild = guild

        # This will increment for as long as the bot idles in a voice channel.
        self.current_idle_time = 0

    def clear(self):
        # TODO: Document this a bit clearer.
        if self.tracks != []:
            self.tracks = [self.tracks[0]]

    def remove_track(self, track_index_to_remove):
        self.tracks.pop(track_index_to_remove)

    # TODO: Will eventually add up the total duration of all tracks
    # in the queue.
    def total_time(self):
        return None

    def add_track(self, track_data):
        self.tracks.append(track_data)

    def pretty_display(self):
        # TODO: Is there a way to clean this up? Like, iterate through a list
        # while incrementing a counter without using range()?
        tracks = []
        if self.is_empty():
            return "Empty queue!"
        else:
            header = msgs.PRETTY_QUEUE_HEADER
            for track in range(0, len(self.tracks)):
                queue_pos = track + 1
                trimmed_title = trim(self.tracks[track].title)
                duration = self.tracks[track].duration
                tracks.append(f"{queue_pos}  {trimmed_title}{duration}  \n")

            return f"```{header}\n{''.join(tracks)}```"
