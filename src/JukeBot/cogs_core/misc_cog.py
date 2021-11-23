"""Defines any miscellaneous commands (currently only !about) and the improved
!help command.
"""
from nextcord.ext import commands
import JukeBot
from JukeBot.utils.embed_dialogs import dialogBox
import JukeBot.messages as msgs


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
                          msgs.ABOUT)
        reply.set_image(url=msgs.BANNER_IMG)
        if not JukeBot.config.RELEASE_VER:
            reply.set_footer(text="JukeBot — Running from source")
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
                          msgs.UPDATE_CHANGELOG)
        reply.set_image(url=msgs.BANNER_IMG)
        reply.set_footer(text=msgs.UPDATE_FOOTER)
        await ctx.send(embed=reply, delete_after=86400)  # 24 hrs
