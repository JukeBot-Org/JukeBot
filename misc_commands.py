import nextcord as discord
from nextcord.ext import commands
from embed_dialogs import DialogBox
import git
import config

class ImprovedHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping): # !help
        print("send_bot_help")
        for cog in mapping:
            await self.get_destination().send("{name}: {uhh}".format(name = cog,
                                                                     uhh  = [command.name for command in mapping[cog]]))
        return await super().send_bot_help(mapping)

    async def send_cog_help(self, cog): # !help CogName
        print("send_cog_help")
        await self.get_destination().send("{name}: {uhh}".format(name = cog,
                                                                 uhh  = [command.name for command in cog.get_commands()]))
        return await super().send_cog_help(cog)

    async def send_command_help(self, command): # !help commandname
        print("send_command_help")
        await self.get_destination().send("{name}: {uhh}".format(name = command.name,
                                                                 uhh  = command.help))
        return await super().send_command_help(command)

class Other(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def about(self, ctx):
        await ctx.message.delete()
        repo      = git.Repo(search_parent_directories=True)
        reply = DialogBox("Version", "Thank you for using JukeBot!",
        """**JukeBot** is a self-hostable music streaming bot that runs on spite, a love for freedom, and Python 3.\n
        You can find more information on the project, as well as the source code to host your own instance of JukeBot, at **https://squigjess.github.io/JukeBot**""")
        reply.set_image(url="https://media.discordapp.net/attachments/891977633275969537/894946455721218068/jukebot.png")
        reply.set_footer(text="JukeBot v.{version} ({branch} branch)".format(version=repo.head.object.hexsha[0:7],
                                                                             branch=repo.head.ref))
        await ctx.send(embed=reply)
