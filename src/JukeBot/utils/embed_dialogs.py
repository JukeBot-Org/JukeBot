"""A wrapper for discord.Embed to aid in creating nice-looking messages using
link-less embeds.
"""
from nextcord import Embed, Colour

JukeBot_Bluegreen = Colour.from_rgb(6, 227, 164)
avatar_url = None
version = None

styles = {#Reason    Which emoji to use       The colour of the accent on the left
          "Warn":    [":warning:",            Colour.yellow()],
          "Error":   [":no_entry_sign:",      Colour.red()],
          "Debug":   [":gear:",               Colour.lighter_grey()],
          "Test":    [":red_circle:",         Colour.red()],
          "Success": [":white_check_mark:",   Colour.green()],
          "Loading": [":hourglass:",          Colour.yellow()],
          # JukeBot-specific styles
          "Help":    [":woman_technologist:", JukeBot_Bluegreen],
          "Playing": [":arrow_forward:",      JukeBot_Bluegreen],
          "Paused":  [":pause_button:",       JukeBot_Bluegreen],
          "Queued":  [":arrow_heading_down:", JukeBot_Bluegreen],
          "Eject":   [":eject:",              JukeBot_Bluegreen],
          "Version": [":green_heart:",        JukeBot_Bluegreen],
          "Skip":    [":track_next:",         JukeBot_Bluegreen]}


def dialogBox(theme, message_title, message_content="", url=None):
    """Creates a nice-looking dialog box using Discord's native embeds."""
    embed_kwargs = {"title":       f"{styles[theme][0]}  {message_title}",
                    "colour":      styles[theme][1],
                    "description": message_content}
    if url:
        embed_kwargs["url"] = url
    return Embed(**embed_kwargs).set_footer(icon_url=avatar_url, text=f"JukeBot v.{version}")
