"""Additional re-usable checks for JukeBot commands."""

from nextcord.ext import commands
from JukeBot.embed_dialogs import dialogBox
import JukeBot

temp_title = "Hang on!"
temp_footer = "This message will automatically disappear shortly."


def is_developer():
    """A command with this check will only run if the user invoking the command
    is a developer of JukeBot.
    """
    async def predicate(ctx):
        return ctx.author.id in [83333350588157952]
    return commands.check(predicate)


def is_playing():
    """A command with this check will only run if JukeBot is currently playing
    audio.
    """
    async def predicate(ctx):
        if ctx.cog.is_playing is False:
            reply = dialogBox("Warn", temp_title, "JukeBot is currently not playing.")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
        return ctx.cog.is_playing
    return commands.check(predicate)


def user_in_vc():
    """A command with this check will only run if the user invoking the command
    is in a voice channel at the time of invocation.
    """
    async def predicate(ctx):
        if ctx.author.voice is None:
            reply = dialogBox("Warn", temp_title, "Connect to a voice channel before issuing the command.")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
            return False
        return True
    return commands.check(predicate)


def jukebot_in_vc():
    """A command with this check will only run if JukeBot is in a voice channel
    at the time of invocation.
    """
    async def predicate(ctx):
        if ctx.cog.voice_channel is None:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot is not in a voice channel at the moment.\nPerhaps try `{JukeBot.config.COMMAND_PREFIX}play`ing a track first?")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
            return False
        return True
    return commands.check(predicate)


def queue_not_empty():
    """A command with this check will only run if JukeBot's track queue
    is not empty.
    """
    async def predicate(ctx):
        if ctx.cog.queue.tracks == []:
            reply = dialogBox("Warn", temp_title,
                              f"The queue is currently empty.\nPerhaps try `{JukeBot.config.COMMAND_PREFIX}play`ing a track first?")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
            return False
        return True
    return commands.check(predicate)


def is_not_paused():
    """A command with this check will only run if JukeBot is currently
    paused.
    """
    async def predicate(ctx):
        if ctx.cog.queue.is_paused is True:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot is already paused.\nType `{JukeBot.config.COMMAND_PREFIX}resume` to resume the track.")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
            return False
        return True
    return commands.check(predicate)


def is_paused():
    """A command with this check will only run if JukeBot is not
    paused. Mainly for use with the !resume command.
    """
    async def predicate(ctx):
        if ctx.cog.queue.is_paused is False:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot isn't paused.\nType `{JukeBot.config.COMMAND_PREFIX}pause` to pause the track.")
            reply.set_footer(text=temp_footer)
            await ctx.reply(embed=reply, delete_after=10)
            return False
        return True
    return commands.check(predicate)
