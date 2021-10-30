from nextcord.ext import commands, tasks
import asyncio

import JukeBot
from JukeBot.embed_dialogs import dialogBox
from JukeBot.utils import humanize_duration


class Tests(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="runtests", hidden=True)
    @JukeBot.checks.user_in_vc()
    @JukeBot.checks.is_developer()
    async def _runtests(self, ctx):
        """**Internal command.**
        Runs semi-automated tests.
        """
        async for message in ctx.channel.history(limit=100):
            await message.delete()
        
        await ctx.send(embed=dialogBox("Test", "Loading example tracks..."))
        await ctx.invoke(self.client.get_command("play"), search_query="doja cat imagine")
        await ctx.invoke(self.client.get_command("play"), search_query="earth wind and fire september")
        await ctx.invoke(self.client.get_command("play"), search_query="earth wind and fire lets groove")
        await ctx.invoke(self.client.get_command("play"), search_query="cult of dionysus the orion experience")
        await ctx.invoke(self.client.get_command("play"), search_query="california soul marlena shaw")
        await ctx.invoke(self.client.get_command("queue"))
        await ctx.send(embed=dialogBox("Test", f"Waiting 5 sec..."))
        await asyncio.sleep(5)

        await ctx.send(embed=dialogBox("Test", f"Trying `{JukeBot.config.COMMAND_PREFIX}skip`..."))
        await ctx.invoke(self.client.get_command("skip"))
        await ctx.invoke(self.client.get_command("queue"))
        await ctx.send(embed=dialogBox("Test", f"Waiting 5 sec..."))
        await asyncio.sleep(5)

        await ctx.send(embed=dialogBox("Test", f"Trying `{JukeBot.config.COMMAND_PREFIX}nowplaying`..."))
        await ctx.invoke(self.client.get_command("nowplaying"))
        await ctx.send(embed=dialogBox("Test", f"Waiting 3 sec..."))
        await asyncio.sleep(3)

        await ctx.send(embed=dialogBox("Test", f"Trying `{JukeBot.config.COMMAND_PREFIX}pause` and `{JukeBot.config.COMMAND_PREFIX}resume`..."))
        await ctx.invoke(self.client.get_command("nowplaying"))
        await ctx.invoke(self.client.get_command("pause"))
        await asyncio.sleep(3)
        await ctx.invoke(self.client.get_command("pause"))
        await asyncio.sleep(3)
        await ctx.invoke(self.client.get_command("resume"))
        await asyncio.sleep(3)
        await ctx.invoke(self.client.get_command("resume"))
        await asyncio.sleep(3)
        await ctx.invoke(self.client.get_command("nowplaying"))

        await ctx.send(embed=dialogBox("Success", "Tests completed."))


    @commands.command(name="tq", hidden=True)
    @JukeBot.checks.user_in_vc()
    @JukeBot.checks.is_developer()
    async def _tq(self, ctx):
        """**Internal command.**
        Loads some example tracks for testing queue-related operations.
        """
        await ctx.send(embed=dialogBox("Debug", "Loading test queue..."))
        await ctx.invoke(self.client.get_command("play"), search_query="doja cat imagine")
        await ctx.invoke(self.client.get_command("play"), search_query="earth wind and fire september")
        await ctx.invoke(self.client.get_command("play"), search_query="cult of dionysus the orion experience")
        await ctx.invoke(self.client.get_command("queue"))
        await ctx.send(embed=dialogBox("Debug", "Test queue finished loading."))


    @commands.command(name="x", hidden=True)
    @JukeBot.checks.user_in_vc()
    @JukeBot.checks.is_developer()
    async def _x(self, ctx):
        """**Internal command.**
        If you accept the definition that a word is some letters
        surrounded by a gap, then...
        """
        await ctx.invoke(self.client.get_command("play"), search_query="tom scott disintegrates xnopyt")

