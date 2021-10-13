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

def dialogBox(message_emoji, message_title, message_content=False):
    """Creates a nice-looking dialog box using Discord's native embeds."""
    title = f"{styles[message_emoji][0]}  {message_title}"
    colour = styles[message_emoji][1]

    if not message_content: # If the dialog box was called without any message content, just a title and an emoji...
        embed = Embed(title = title,
                      colour = colour)
    else: # If we got an emoji, a title, _and_ message text.
        embed = Embed(title = title,
                      description = message_content,
                      colour = colour)
    return embed
