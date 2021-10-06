import nextcord as discord
from nextcord.ext import commands
from embed_dialogs import DialogBox
import git
import config

def docstring_scrubber(original, KeepExamples=False):
    proper_prefix = original.replace("<prefix>", config.COMMAND_PREFIX)
    if KeepExamples:
        final = proper_prefix
    else:
        final = proper_prefix.split("**Examples**")[0]
    return final

class ImprovedHelp(commands.HelpCommand): # A much nicer-looking !help command
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping): # !help
        embed = DialogBox("Help", "How to use JukeBot", f"Type `{config.COMMAND_PREFIX}help commandname` for more help on a specific command.")
        for cog in mapping: # For each cog, we go through and add it to the embed dialog.
            if cog != None:
                cog_name = cog.qualified_name
            else: # The help command's cog type is None. We check to avoid an exception.
                cog_name = "System"

            embed.add_field(name=f"Category: {cog_name}",
                            value="".join([config.COMMAND_PREFIX+command.name+"\n" for command in mapping[cog]]),
                            inline=False)

        await self.get_destination().send(embed=embed)
        return await super().send_bot_help(mapping)


    async def send_cog_help(self, cog): # !help CategoryName
        embed = DialogBox("Help", f"How to use JukeBot: {cog.qualified_name} commands")

        for command in cog.get_commands():
            embed.add_field(name="{config.COMMAND_PREFIX}{command.name}",
                            value=docstring_scrubber(command.help),
                            inline=False)

        await self.get_destination().send(embed=embed)
        return await super().send_cog_help(cog)


    async def send_command_help(self, command): # !help commandname
        help_string = docstring_scrubber(command.help, KeepExamples=True)
        embed = DialogBox("Help", "How to use JukeBot", "**{config.COMMAND_PREFIX}{command.name}** — {help_string}")
        await self.get_destination().send(embed=embed)
        return await super().send_command_help(command)

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def about(self, ctx):
        """Displays info about the bot, including version number and a link to the project website."""
        await ctx.message.delete()
        reply = DialogBox("Version", "Thank you for using JukeBot!",
        """**JukeBot** is a self-hostable music streaming bot that runs on spite, a love for freedom, and Python 3.\n
        You can find more information on the project, as well as the source code to host your own instance of JukeBot, at **https://squigjess.github.io/JukeBot**""")
        reply.set_image(url="https://media.discordapp.net/attachments/887723918574645331/895242544223518740/discordjp.jpg")

        try:
            repo = git.Repo(search_parent_directories=True)
            version = repo.head.object.hexsha[0:7],
            branch = repo.head.ref
            reply.set_footer(text=f"JukeBot v.{version} ({branch} branch)")
        # If the code is just downloaded with no git data, stop the command from breaking.
        except git.exc.InvalidGitRepositoryError:
            reply.set_footer(text="JukeBot — https://github.com/squigjess/JukeBot")

        await ctx.send(embed=reply)
