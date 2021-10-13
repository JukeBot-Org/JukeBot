"""A wrapper for discord.Embed to aid in creating nice-looking messages using
link-less embeds.
"""
from nextcord import Embed, Colour

JukeBot_Bluegreen = Colour.from_rgb(6, 227, 164)

styles = {#Reason      Which emoji to use      The colour of the accent on the left
          "Warn"    : [":warning:",            Colour.yellow()],
          "Error"   : [":no_entry_sign:",      Colour.red()],
          "Playing" : [":arrow_forward:",      JukeBot_Bluegreen],
          "Queued"  : [":speech_balloon:",     JukeBot_Bluegreen],
          "Version" : [":green_heart:",        JukeBot_Bluegreen],
          "Help"    : [":woman_technologist:", JukeBot_Bluegreen],
          "Skip"    : [":track_next:",         JukeBot_Bluegreen],
          "Debug"   : [":gear:",               Colour.lighter_grey()]}

def dialogBox(theme, message_title, message_content="", url=None):
    """Creates a nice-looking dialog box using Discord's native embeds."""
    embed_kwargs = {"title"       : f"{styles[theme][0]}  {message_title}",
                    "colour"      : styles[theme][1],
                    "description" : message_content}
    if url:
        embed_kwargs["url"] = url
    return Embed(**embed_kwargs)
