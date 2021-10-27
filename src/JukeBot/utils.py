"""Utility functions used sporadically across JukeBot."""
import datetime


def humanize_duration(total_seconds):
    hours, remainder = divmod(int(total_seconds), 60 * 60)
    minutes, seconds = divmod(remainder, 60)
    final_representation = (f"{hours} hr " if hours > 0 else "") + (f"{minutes} min " if minutes > 0 else "") + f"{seconds} sec "
    return final_representation


def trim(name: str):
    """Takes a song title and truncates or extends it to final_length chars in
    length if need be. Used specifically to fit longer song titles into the
    output of the !queue command.
    """
    final_length = 53
    trimmed = ""

    if len(name) > final_length - 1:
        trimmed = name[:final_length - 3] + '...'
    else:
        trimmed = name

    padding_amt = (final_length + 2) - len(trimmed)
    padding = " " * padding_amt
    return f"{trimmed}{padding}"
