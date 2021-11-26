import JukeBot.config

EPHEMERAL_FOOTER = "This message will automatically disappear shortly"

CANNOT_PLAY = ("**Possible reasons:**\n"
               "- Incorrect video format\n"
               "- No results for search query\n"
               "- Streaming disabled by YouTube uploader\n"
               "- Malformed or invalid link provided.")

NO_SPOTIFY = ("Please put your Spotify application's Client ID and Client "
              "Secret into `JukeBot.config`. Without this, JukeBot cannot "
              "access the Spotify API.\n\n"
              "Please see [this link](http://google.com/) for more "
              "information on setting up Spotify integration for JukeBot.")

PRETTY_QUEUE_HEADER = "#  Track title                                            Duration "

PLS_RESUME = f"Type `{JukeBot.config.COMMAND_PREFIX}resume` to resume the track."

UPDATE_FOOTER = "This update message will automatically disappear after 24 hrs.\n\nhttp://JukeBot-Org.github.io/JukeBot"

BANNER_IMG = "https://media.discordapp.net/attachments/887723918574645331/895242544223518740/discordjp.jpg"
THUMB_IMG = "https://cdn.discordapp.com/avatars/886200359054344193/4da9c1e1257116f08c99c904373b47b7.png"

# =============================== LENGTHY BOIS ============================== #

ABOUT = """**JukeBot** is a self-hostable audio streaming bot that runs on spite, a love for freedom, and Python 3.\n
You can find more information on the project, as well as download the program to host your own instance of JukeBot, at **https://JukeBot-Org.github.io/JukeBot**

Please keep in mind that JukeBot is still a work-in-progress! I guess you could say it's \"in alpha\". If you're currently lucky enough to have JukeBot running in your server, expect there to be some hiccups and bugs - report them to https://github.com/JukeBot-Org/JukeBot/issues if you see any!"""

UPDATE_CHANGELOG = """**Thank you for helping test out JukeBot while I still work on it!**\n
**This is quite a milestone update; a lot of changes have been implemented, bringing JukeBot closer to being a fully-stable audio streaming bot!**
    - A bunch of major bugs have been fixed.
    - New commands are here - `!pause`, `!resume`, `!nowplaying`, and `!stop`/`!disconnect`.
    - You can now remove individual tracks from the queue with `!clear x`, where `x` is the number of the track in the queue (see `!queue`).
    - Heaps of bugs fixed.
    - If you have multiple Discord servers in which you would like to run your copy of JukeBot, that's now possible! I mean, it was _always_ possible, it just didnt't work. At all.
    - The auto-disconnect feature is back after being temporarily disabled for a minute.
    - No I mean there were a **lot** of bugs in the previous alpha version. Christ alive, it was bad.

Currently, I'm working on the Spotify integration problem and the ability to save queues. Hold tight!

_As you jam out, please keep in mind that JukeBot is still a work-in-progress. If you're currently lucky enough to have JukeBot running in your server, expect there to be some hiccups and bugs - please report them to me on Discord at squig#1312, or via the ticket system at https://github.com/JukeBot-Org/JukeBot/issues if you see any._"""
