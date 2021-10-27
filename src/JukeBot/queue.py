"""Defines how queue data is stored."""
from JukeBot.utils import trim


class Queue:
    def __init__(self):
        self.tracks = []
        self.is_empty = lambda: not bool(self.tracks)  # lmfao
        self.is_paused = False

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
