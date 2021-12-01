import nextcord
from nextcord.ext import commands
import os
import JukeBot
import JukeBot.Messages as msgs
from JukeBot.Utils.embed_dialogs import dialogBox


class Admin(commands.Cog):
    """Commands for administration, management, etc. Can typically only be used
       by the server owner or the bot owner.
    """
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def logs(self, ctx, all_logs=None):
        """**Internal command, bot owner only.**
        Collects JukeBot's recent logs and DMs them to you.

        **Examples**
        `<prefix>logs` takes either one or zero parameters. If the command is
        invoked as `<prefix>logs all`, the five most recent logs will be sent.
        If the command is invoked as simply `<prefix>logs`, only the current
        session's logs will be sent.
        """
        await ctx.message.delete()
        log_file = []
        if all_logs == "all":
            for log in os.listdir(JukeBot.config.LOG_FILE_DIR)[-5:]:
                log_path = os.path.join(JukeBot.config.LOG_FILE_DIR, log)
                log_file.append(nextcord.File(open(log_path, "rb"),
                                              filename=os.fsdecode(log)))
        else:
            log_file.append(nextcord.File(open(JukeBot.config.LOG_FILE_PATH, "rb"),
                            filename=JukeBot.config.LOG_FILE_NAME))
        reply = dialogBox("Debug", "Sending logs via DM...").set_footer(text=msgs.EPHEMERAL_FOOTER)
        await ctx.send(embed=reply, delete_after=5)
        await ctx.author.send("`Your JukeBot logs, as requested:`", files=log_file)

    @commands.command()
    @JukeBot.checks.is_developer()
    async def update(self, ctx):
        """**Internal command.**
        Provides update messages and changelogs to alpha testers' servers.
        """
        await ctx.message.delete()
        reply = dialogBox("Version", "JukeBot has been updated!",
                          msgs.UPDATE_CHANGELOG)
        reply.set_image(url=msgs.BANNER_IMG)
        reply.set_footer(text=msgs.UPDATE_FOOTER)
        await ctx.send(embed=reply, delete_after=86400)  # 24 hrs
