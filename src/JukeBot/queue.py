from JukeBot.utils import trim
import nextcord


class Queue:
    def __init__(self, guild: nextcord.Guild):
        self.tracks = []  # Stores an ordered list of the tracks in the queue. 0th is playing currently, 1st is next, and so on.
        self.is_empty = lambda: not bool(self.tracks)  # lmfao
        self.is_playing = False  # Tracks if the bot is playing. Need to remove this in favour of built-in nextcord equivalent.
        self.audio_player = None  # A nextcord.VoiceChannel object representing the VC we're in currently.
        self.guild = guild  # A nextcord.Guild object that contains info about the guild which this queue is for.
        self.current_idle_time = 0  # This will increment for as long as the bot idles in a voice channel.

    def clear(self):
        self.tracks = []

    def remove_track(self, track_index_to_remove):
        self.tracks.pop(track_index_to_remove)

    def total_time(self):
        return None  # Will eventually add up the total duration of all tracks in the queue.

    def add_track(self, track_data):
        self.tracks.append(track_data)

    def pretty_display(self):
        # TODO: Is there a way to clean this up? Like, iterate through a list
        # while incrementing a counter without using range()?
        tracks = []
        if self.is_empty():
            return "Empty queue!"
        else:
            header = "#  Track title                                            Duration "
            for track in range(0, len(self.tracks)):
                queue_pos = track + 1
                trimmed_title = trim(self.tracks[track].title)
                duration = self.tracks[track].duration
                tracks.append(f"{queue_pos}  {trimmed_title}{duration}  \n")

            return f"`{header}\n{''.join(tracks)}`"
