from nextcord.ext import commands
import JukeBot
import JukeBot.Messages as msgs
from JukeBot.Utils.embed_dialogs import dialogBox


def docstring_scrubber(original):
    """Takes a docstring and splits out the examples section from the command
    help details.
    """
    full = original.replace("<prefix>", JukeBot.Config.COMMAND_PREFIX)
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
    `<prefix>usercheck` takes X parameters. Explain each parameter in detail
    in a layman-ised fashion. If the command takes no parameters, omit this
    section.
    Three examples of a command are good. It's preferable to include examples
    that demonstrate any quirks mentioned above.

    `<prefix>commandname`
    `<prefix>commandname arg1`
    `<prefix>commandname arg1 arg2` (it's fine to clarify functional
                                    differences in parentheses here)

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
        embed = dialogBox("Help", f"How to use {self.app_name}",
                          f"Type `{JukeBot.Config.COMMAND_PREFIX}help commandname` for more help on a specific command.")

        # For each cog, we go through and add it as a field to the embed dialog.
        # The !help commands does not belong to a cog and therefore has no type.
        # Therefore we check to avoid an exception and instead add it to a dummy group.
        for cog in mapping:
            if cog is not None:
                cog_name = cog.qualified_name
            else:
                cog_name = "System"

            all_cmds_in_cog = "".join([JukeBot.Config.COMMAND_PREFIX + command.name + "\n" for command in mapping[cog]])
            embed.add_field(name=f"Category: {cog_name}",
                            value=all_cmds_in_cog,
                            inline=False)
        embed.set_thumbnail(url=msgs.THUMB_IMG)
        await self.get_destination().send(embed=embed)
        return await super().send_bot_help(mapping)

    async def send_cog_help(self, cog):
        """Triggers on !help CogName, provides truncated instructions for all commands in a specified cog."""
        embed = dialogBox("Help", f"How to use {self.app_name}: {cog.qualified_name} commands")

        for command in cog.get_commands():
            synopsis, full, truncated = docstring_scrubber(command.help)
            embed.add_field(name=f"{JukeBot.Config.COMMAND_PREFIX}{command.name} — {synopsis}",
                            value=truncated,
                            inline=False)
        embed.set_thumbnail(url=msgs.THUMB_IMG)
        await self.get_destination().send(embed=embed)
        return await super().send_cog_help(cog)

    async def send_command_help(self, command):
        """Triggers on !help commandname, provides full instructions for the specified command."""
        synopsis, full, truncated = docstring_scrubber(command.help)
        embed = dialogBox("Help", f"How to use {self.app_name}",
                          f"**{JukeBot.Config.COMMAND_PREFIX}{command.name}** — {full}")
        embed.set_thumbnail(url=msgs.THUMB_IMG)
        await self.get_destination().send(embed=embed)
        return await super().send_command_help(command)
