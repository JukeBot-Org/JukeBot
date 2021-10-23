"""Defines how queue data is stored."""

class Queue:
    def __init__(self):
        self.tracks = []
        self.is_empty = lambda: not bool(self.tracks) #lmfao

    def clear(self):
        self.tracks = []

    def remove_track(self, track_index_to_remove):
        self.tracks.pop(track_index_to_remove)

    def total_time(self):
        return None # Will eventually add up the total duration of all tracks in the queue.

    def add_track(self, track_data):
        self.tracks.append(track_data)

    def track(self, track_number):
        return None