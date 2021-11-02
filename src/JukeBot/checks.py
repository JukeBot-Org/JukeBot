"""Additional re-usable checks for JukeBot commands."""

from nextcord.ext import commands
from JukeBot.embed_dialogs import dialogBox
import JukeBot

temp_title = "Hang on!"
temp_footer = "This message will automatically disappear shortly."
visible_time = 10  # seconds. Warnings will vanish after this.


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
        if ctx.cog.all_queues[ctx.guild.id].is_playing is False:
            reply = dialogBox("Warn", temp_title, "JukeBot is currently not playing.")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
        return ctx.cog.all_queues[ctx.guild.id].is_playing
    return commands.check(predicate)


def user_in_vc():
    """A command with this check will only run if the user invoking the command
    is in a voice channel at the time of invocation.
    """
    async def predicate(ctx):
        if ctx.author.voice is None:
            reply = dialogBox("Warn", temp_title, "Connect to a voice channel before issuing the command.")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
            return False
        return True
    return commands.check(predicate)


def jukebot_in_vc():
    """A command with this check will only run if JukeBot is in a voice channel
    at the time of invocation.
    """
    async def predicate(ctx):
        await set_up_guild_queue(None, ctx)  # Don't ask
        if ctx.cog.all_queues[ctx.guild.id].audio_player is None:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot is not in a voice channel at the moment.\nPerhaps try `{JukeBot.config.COMMAND_PREFIX}play`ing a track first?")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
            return False

        return True
    return commands.check(predicate)


def queue_not_empty():
    """A command with this check will only run if JukeBot's track queue
    is not empty.
    """
    async def predicate(ctx):
        if ctx.cog.all_queues[ctx.guild.id].tracks == []:
            reply = dialogBox("Warn", temp_title,
                              f"The queue is currently empty.\nPerhaps try `{JukeBot.config.COMMAND_PREFIX}play`ing a track first?")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
            return False

        return True
    return commands.check(predicate)


def is_not_paused():
    """A command with this check will only run if JukeBot is currently
    paused.
    """
    async def predicate(ctx):
        print(ctx.cog.all_queues[ctx.guild.id].audio_player.is_paused())
        if ctx.cog.all_queues[ctx.guild.id].audio_player.is_paused() is True:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot is already paused.\nType `{JukeBot.config.COMMAND_PREFIX}resume` to resume the track.")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
            return False
        return True
    return commands.check(predicate)


def is_paused():
    """A command with this check will only run if JukeBot is not
    paused. Mainly for use with the !resume command.
    """
    async def predicate(ctx):
        print(ctx.cog.all_queues[ctx.guild.id].audio_player.is_paused())
        if ctx.cog.all_queues[ctx.guild.id].audio_player.is_paused() is False:
            reply = dialogBox("Warn", temp_title,
                              f"JukeBot isn't paused.\nType `{JukeBot.config.COMMAND_PREFIX}pause` to pause the track.")
            reply.set_footer(text=temp_footer)
            await ctx.send(embed=reply, delete_after=visible_time)
            return False
        return True
    return commands.check(predicate)


# This is not actually a check that can be used with a decorator like usual.
# This is actually called in an on_command_error listener.
async def argument_is_missing(ctx):
    command_attempted = JukeBot.config.COMMAND_PREFIX + ctx.command.name
    help_for_command = f"{JukeBot.config.COMMAND_PREFIX}help {ctx.command.name}"
    reply = dialogBox("Warn", temp_title,
                      f"Missing argument for command `{command_attempted}`.\nType `{help_for_command}` for info on how to use this command.")
    reply.set_footer(text=temp_footer)
    await ctx.send(embed=reply, delete_after=visible_time)


# This is not actually a check that can be used with a decorator like usual.
# This is actually called in an on_command_error listener.
async def command_not_found(ctx):
    command_attempted = JukeBot.config.COMMAND_PREFIX + ctx.message.content[1:]
    help_command = f"{JukeBot.config.COMMAND_PREFIX}help"
    reply = dialogBox("Warn", temp_title,
                      f"Command not found: `{command_attempted}`.\nType `{help_command}` for a list of commands you can use.")
    reply.set_footer(text=temp_footer)
    await ctx.send(embed=reply, delete_after=6)


# This is not actually a check that can be used with a decorator like usual, but is instead
# a pre-invoke hook - https://nextcord.readthedocs.io/en/latest/ext/commands/api.html#nextcord.ext.commands.Command.before_invoke
async def set_up_guild_queue(cog, ctx):
    if ctx.guild.id not in ctx.cog.all_queues:
        ctx.cog.all_queues[ctx.guild.id] = JukeBot.Queue()