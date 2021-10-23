"""Additional re-usable checks for JukeBot commands."""

from nextcord.ext import commands

def is_developer():
    async def predicate(ctx):
        return ctx.author.id in [83333350588157952]
    return commands.check(predicate)