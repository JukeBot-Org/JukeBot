"""Defines any miscellaneous commands (currently only !about) and the improved
!help command.
"""
import nextcord as discord
from nextcord.ext import commands

import config
from embed_dialogs import DialogBox

def docstring_scrubber(original, KeepExamples=False):
    """Takes a docstring and splits out the examples section from the command
    help details. Really only used by ImprovedHelp().
    """
    proper_prefix = original.replace("<prefix>", config.COMMAND_PREFIX)
    if KeepExamples:
        final = proper_prefix
    else:
        final = proper_prefix.split("**Examples**")[0]
    return final

class ImprovedHelp(commands.HelpCommand):
    """A much nicer !help command that uses Discord embeds to generate a more
    easily grokkable experience for end users. See below for the syntax that
    your command docstrings should follow in order to work with this function.
    Requires embed_dialogs.py in order to function, otherwise this is a drop-in
    class that can be used as-is in most discord.py/nextcord projects
    ---------------------------------------------------------------------------

    '''**One-line explanation of what the command does.**
    `<prefix>commandname` performs a certain task. Make sure to explain with
    adequate detail what the command does and any quirks it may have.

    **Examples**
    `<prefix>usercheck` takes X arguments. Explain each argument in detail in a
    layman-ised fashion. If the command takes no arguments, omit this section.
    Three examples of a command are good. It's preferable to include examples
    that demonstrate any quirks mentioned above.

    `<prefix>commandname`
    `<prefix>commandname arg1`
    `<prefix>commandname arg1 arg2` (it's fine to clarify differences in
                                    function in parentheses here)

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

    async def send_bot_help(self, mapping): # !help
        """Triggers on !help, provides command names for all commands in this bot."""
        embed = DialogBox("Help", f"How to use {self.app_name}", f"Type `{config.COMMAND_PREFIX}help commandname` for more help on a specific command.")

        # For each cog, we go through and add it as a field to the embed dialog.
        # The !help commands does not belong to a cog and therefore has no type.
        # Therefore we check to avoid an exception and instead add it to a dummy group.
        for cog in mapping:
            if cog != None:
                cog_name = cog.qualified_name
            else:
                cog_name = "System"

            embed.add_field(name=f"Category: {cog_name}",
                            value="".join([config.COMMAND_PREFIX+command.name+"\n" for command in mapping[cog]]),
                            inline=False)
        await self.get_destination().send(embed=embed)
        return await super().send_bot_help(mapping)


    async def send_cog_help(self, cog):
        """Triggers on !help CogName, provides truncated instructions for all commands in a specified cog."""
        embed = DialogBox("Help", f"How to use {self.app_name}: {cog.qualified_name} commands")

        for command in cog.get_commands():
            embed.add_field(name=f"{config.COMMAND_PREFIX}{command.name}",
                            value=docstring_scrubber(command.help),
                            inline=False)
        await self.get_destination().send(embed=embed)
        return await super().send_cog_help(cog)


    async def send_command_help(self, command):
        """Triggers on !help commandname, provides full instructions for the specified command."""
        help_string = docstring_scrubber(command.help, KeepExamples=True)
        embed = DialogBox("Help", f"How to use {self.app_name}", f"**{config.COMMAND_PREFIX}{command.name}** — {help_string}")
        await self.get_destination().send(embed=embed)
        return await super().send_command_help(command)

class Other(commands.Cog):
    """Commands that do not fit into the Music cog, i.e. those that handle
    settings, application info, etc.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def about(self, ctx):
        """"""
        """**Displays info about the bot, including version number and a link
        to the project website.**
        `<prefix>about` simply displays gratitude from the developer(s) to
        you, the users. It also displays version info and a link to the project
        website if you ever need it.

        **Examples**
        `<prefix>about`
        """
        reply = DialogBox("Version", "Thank you for using JukeBot!",
        """**JukeBot** is a self-hostable music streaming bot that runs on spite, a love for freedom, and Python 3.\n
        You can find more information on the project, as well as download the program to host your own instance of JukeBot, at **https://squigjess.github.io/JukeBot**

        Please keep in mind that JukeBot is still a work-in-progress! I guess you'd say it's \"in alpha\". If you're currently lucky enough to have JukeBot running in your server, expect there te be some hiccups and bugs - report them to https://github.com/squigjess/JukeBot/issues if you see any!""")
        reply.set_image(url="https://media.discordapp.net/attachments/887723918574645331/895242544223518740/discordjp.jpg")
        if not GIT_VER: # If we're currently running the bot from source in testing...
            reply.set_footer(text=f"JukeBot — Running from source, unknown version")
        else: # If this is a live release version...
            reply.set_footer(text=f"JukeBot — v.{GIT_VER} (FINAL LIVE build)")

        await ctx.send(embed=reply)
# This var must be left as `None`, otherwise the build will fail.
# lmfao
GIT_VER=None
