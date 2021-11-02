#!/usr/bin/env python3
"""The main entry point for JukeBot. Instantiates the bot (as client),
initialises libraries, handles error logging.
"""
import nextcord
from nextcord.ext import commands
import sys
import os
import colorama
from colorama import Fore as fg
from colorama import Style as st
import logging

import JukeBot

client = commands.Bot(command_prefix=JukeBot.config.COMMAND_PREFIX,
                      help_command=JukeBot.misc_commands.ImprovedHelp())


def initialise():
    """Initialises Opus (on non-Windows platforms), Colorama, the log file for
    this session, etc.
    """
    colorama.init()

    if not os.path.exists(JukeBot.config.LOG_FILE_DIR):
        print(f"{fg.YELLOW}Logs directory missing. Creating...{st.RESET_ALL}")
        os.mkdir(JukeBot.config.LOG_FILE_DIR)
        print(f"{fg.GREEN}Created.{st.RESET_ALL}\n")

    logging.basicConfig(filename=JukeBot.config.LOG_FILE_PATH,
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s:%(message)s")

    if sys.platform == "win32":
        print(f"{fg.YELLOW}Manually loading Opus not necessary, skipping.{st.RESET_ALL}")
    else:
        print(f"{fg.YELLOW}Need to manually load Opus...{st.RESET_ALL}")
        import ctypes
        import ctypes.util
        print("Finding Opus library...")
        opus_loc = ctypes.util.find_library('opus')
        print("Loading Opus...")
        nextcord.opus.load_opus(opus_loc)
        print("Checking if Opus is loaded...")
        if nextcord.opus.is_loaded():
            print(f"{fg.GREEN}Opus module loaded successfully.{st.RESET_ALL}")
        else:
            print(f"{fg.RED}Opus not loaded! Audio may not work.{st.RESET_ALL}")


# Begin handling Discord bot stuff
@client.event
async def on_ready():
    print(f"{fg.GREEN}Logged in{st.RESET_ALL} as {client.user}.")
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening,
                                                            name=JukeBot.config.LISTENING_TO))  # Listening to !help
    client.add_cog(JukeBot.audio_commands.Audio(client))
    client.add_cog(JukeBot.misc_commands.Other(client))
    print(f"{fg.GREEN}Bot is ready!{st.RESET_ALL} Command prefix is {fg.GREEN}{JukeBot.config.COMMAND_PREFIX}{st.RESET_ALL}\n")
    print(f"Press {fg.YELLOW}Ctrl+C{st.RESET_ALL} to safely shut down JukeBot.\n")


@client.event  # Handles errors in nextcord commands
async def on_command_error(ctx, error):
    if type(error) == commands.MissingRequiredArgument:
        await JukeBot.checks.argument_is_missing(ctx)
        return

    if type(error) == commands.CheckFailure:
        return  # No need to raise an exception and clog up the user's logfiles.

    if type(error) == commands.CommandNotFound:
        await JukeBot.checks.command_not_found(ctx)
        return

    logging.error("=====================================================================================")
    logging.error("UNHANDLED COMMAND ERROR, PLEASE REPORT TO https://github.com/squigjess/JukeBot/issues", exc_info=error)
    logging.error("=====================================================================================")
    raise error


if __name__ == "__main__":
    try:
        initialise()
        print(f"\n{fg.YELLOW}Logging in...{st.RESET_ALL}")
        client.run(JukeBot.config.DISCORD_BOT_TOKEN)  # Hello, world!

    except Exception as error:  # Handles non-command errors
        logging.error("=====================================================================================")
        logging.exception("UNHANDLED GENERIC ERROR, PLEASE REPORT TO https://github.com/squigjess/JukeBot/issues")
        logging.error("=====================================================================================")
        raise error
