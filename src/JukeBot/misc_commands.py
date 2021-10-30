"""Defines any miscellaneous commands (currently only !about) and the improved
!help command.
"""
from nextcord.ext import commands
import time
import JukeBot
from JukeBot.embed_dialogs import dialogBox


def docstring_scrubber(original):
    """Takes a docstring and splits out the examples section from the command
    help details. Really only used by ImprovedHelp().
    """
    full = original.replace("<prefix>", JukeBot.config.COMMAND_PREFIX)
    synopsis = full.split("\n", 1)[0]
    truncated = full.split("\n", 1)[1].split("**Examples**")[0]
    return [synopsis, full, truncated]


class ImprovedHelp(commands.HelpCommand):
    """A much nicer !help command that uses Discord embeds to generate a more
    easily grokkable experience for end users. See below for the syntax that
    your command docstrings should follow in order to work with this function.
    Requires embed_dialogs.py in order to function, otherwise this is a
    drop-in class that can be used as-is in most discord.py/nextcord projects.
    ---------------------------------------------------------------------------

    '''**One-line explanation of what the command does.**
    `<prefix>commandname` performs a certain task. Make sure to explain with
    adequate detail what the command does and any quirks it may have.

    **Examples**
    `<prefix>usercheck` takes X parameters. Explain each parameter in detail in a
    layman-ised fashion. If the command takes no parameters, omit this section.
    Three examples of a command are good. It's preferable to include examples
    that demonstrate any quirks mentioned above.

    `<prefix>commandname`
    `<prefix>commandname arg1`
    `<prefix>commandname arg1 arg2` (it's fine to clarify functional differences
                                    in parentheses here)

    **Aliases** — **<prefix>commandname** can also be invoked with:
    `<prefix>commandalias1`
    `<prefix>commandalias2`
    `<prefix>commandalias3`
    (the Aliases section can be left out if a command has none)
    '''
    ---------------------------------------------------------------------------
    """
    def __init__(self, app_name="JukeBot"):
        super().__init__()
        self.app_name = app_name

    async def send_bot_help(self, mapping):  # !help
        """Triggers on !help, provides command names for all commands in this bot."""
        embed = dialogBox("Help", f"How to use {self.app_name}", f"Type `{JukeBot.config.COMMAND_PREFIX}help commandname` for more help on a specific command.")

        # For each cog, we go through and add it as a field to the embed dialog.
        # The !help commands does not belong to a cog and therefore has no type.
        # Therefore we check to avoid an exception and instead add it to a dummy group.
        for cog in mapping:
            if cog is not None:
                cog_name = cog.qualified_name
            else:
                cog_name = "System"

            embed.add_field(name=f"Category: {cog_name}",
                            value="".join([JukeBot.config.COMMAND_PREFIX + command.name + "\n" for command in mapping[cog]]),
                            inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/886200359054344193/4da9c1e1257116f08c99c904373b47b7.png")
        await self.get_destination().send(embed=embed)
        return await super().send_bot_help(mapping)

    async def send_cog_help(self, cog):
        """Triggers on !help CogName, provides truncated instructions for all commands in a specified cog."""
        embed = dialogBox("Help", f"How to use {self.app_name}: {cog.qualified_name} commands")

        for command in cog.get_commands():
            synopsis, full, truncated = docstring_scrubber(command.help)
            embed.add_field(name=f"{JukeBot.config.COMMAND_PREFIX}{command.name} — {synopsis}",
                            value=truncated,
                            inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/886200359054344193/4da9c1e1257116f08c99c904373b47b7.png")
        await self.get_destination().send(embed=embed)
        return await super().send_cog_help(cog)

    async def send_command_help(self, command):
        """Triggers on !help commandname, provides full instructions for the specified command."""
        synopsis, full, truncated = docstring_scrubber(command.help)
        embed = dialogBox("Help", f"How to use {self.app_name}", f"**{JukeBot.config.COMMAND_PREFIX}{command.name}** — {full}")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/886200359054344193/4da9c1e1257116f08c99c904373b47b7.png")
        await self.get_destination().send(embed=embed)
        return await super().send_command_help(command)


class Other(commands.Cog):
    """Commands that do not fit into the Audio cog, i.e. those that handle
    settings, application info, etc.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def about(self, ctx):
        """**Displays info about the bot, including version number and a link
        to the project website.**
        `<prefix>about` simply displays gratitude from the developer(s) to
        you, the users. It also displays version info and a link to the project
        website if you ever need it.

        **Examples**
        `<prefix>about`
        """
        reply = dialogBox("Version", "Thank you for using JukeBot!",
        """**JukeBot** is a self-hostable audio streaming bot that runs on spite, a love for freedom, and Python 3.\n
        You can find more information on the project, as well as download the program to host your own instance of JukeBot, at **https://squigjess.github.io/JukeBot**

        Please keep in mind that JukeBot is still a work-in-progress! I guess you could say it's \"in alpha\". If you're currently lucky enough to have JukeBot running in your server, expect there to be some hiccups and bugs - report them to https://github.com/squigjess/JukeBot/issues if you see any!""")
        reply.set_image(url="https://media.discordapp.net/attachments/887723918574645331/895242544223518740/discordjp.jpg")
        if not JukeBot.config.RELEASE_VER:  # If we're currently running the bot from source in testing...
            reply.set_footer(text=f"JukeBot — Running from source, unknown version")
        else:  # If this is a live release version...
            reply.set_footer(text=f"JukeBot — v.{JukeBot.config.RELEASE_VER}")

        await ctx.send(embed=reply)

    @commands.command()
    @JukeBot.checks.is_developer()
    async def update(self, ctx):
        await ctx.message.delete()
        """**Internal command.**
        Provides update messages and changelogs to alpha testers' servers.
        """
        reply = dialogBox("Version", "JukeBot has been updated!",
        """**Thank you for helping test out JukeBot while I still work on it!**\n
        **This is quite a milestone update; a lot of changes have been implemented, bringing JukeBot closer to being a fully-stable audio streaming bot!**
          - A bunch of major bugs have been fixed.
          - New commands are here - `!pause`, `!resume`, `!nowplaying`, and `!stop`/`!disconnect`.
          - You can now remove individual tracks from the queue with `!clear x`, where `x` is the number of the track in the queue (see `!queue`).
        
        Currently, I'm working on the Spotify integration problem and the ability to save queues. Hold tight!

        _As you jam out, please keep in mind that JukeBot is still a work-in-progress. If you're currently lucky enough to have JukeBot running in your server, expect there to be some hiccups and bugs - please report them to me on Discord at squig#1312, or via the ticket system at https://github.com/squigjess/JukeBot/issues if you see any._""")
        reply.set_image(url="https://media.discordapp.net/attachments/887723918574645331/895242544223518740/discordjp.jpg")
        reply.set_footer(text="This update message will automatically disappear after 24 hrs.\n\nhttp://squigjess.github.io/JukeBot")
        await ctx.send(embed=reply, delete_after=86400)  # 24 hrs
