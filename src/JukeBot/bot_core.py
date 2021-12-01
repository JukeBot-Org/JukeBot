"""The main entry point for JukeBot. This module instantiates the bot (as
client)
"""
import nextcord
from nextcord.ext import commands
import JukeBot

from sys import platform
import os
from colorama import Fore as fg
from colorama import Style as st
import logging

client = commands.Bot(command_prefix=JukeBot.Config.COMMAND_PREFIX,
                      help_command=JukeBot.Utils.help.ImprovedHelp())  # TODO: move to own module


def initialise_preready():
    """Initialises a bunch of stuff before JukeBot attempts to log in to
    Discord.
    """
    print(f"{fg.YELLOW}Pre-login init...{st.RESET_ALL}")

    # Set up logging
    if not os.path.exists(JukeBot.Config.LOG_FILE_DIR):
        print(f"    {fg.YELLOW}Logs directory missing. Creating...{st.RESET_ALL}")
        os.mkdir(JukeBot.Config.LOG_FILE_DIR)
        print(f"    {fg.GREEN}Created.{st.RESET_ALL}\n")
    logging.basicConfig(filename=JukeBot.Config.LOG_FILE_PATH,
                        level=logging.INFO,
                        format="%(asctime)s %(levelname)s:%(message)s")

    # Load Opus on non-Windows systems
    if platform != "win32":
        print(f"    {fg.YELLOW}Need to manually load Opus...{st.RESET_ALL}")
        import ctypes
        import ctypes.util
        print("    Finding Opus library...")
        opus_loc = ctypes.util.find_library('opus')
        print("    Loading Opus...")
        nextcord.opus.load_opus(opus_loc)
        print("    Checking if Opus is loaded...")
        if nextcord.opus.is_loaded():
            print("    Opus module loaded successfully.")
        else:
            print(f"    {fg.RED}Opus not loaded! Audio may not work.{st.RESET_ALL}")
            logging.info("Opus not loaded! Audio may not work.")
    print(f"{fg.GREEN}Completed{st.RESET_ALL}")


def initialise_onceready():
    """Initialises bot's activity status, cogs, etc. once the bot is logged
    in to Discord.
    """
    print(f"\n{fg.YELLOW}Post-login init...{st.RESET_ALL}")
    print(f"    {fg.YELLOW}Loading core cogs...{st.RESET_ALL}")
    client.add_cog(JukeBot.Cogs.Audio(client))
    client.add_cog(JukeBot.Cogs.Misc(client))
    client.add_cog(JukeBot.Cogs.Admin(client))
    for cog in client.cogs:
        print(f"    {cog} cog loaded.")
    JukeBot.Utils.embed_dialogs.avatar_url = client.user.avatar.url
    print(f"{fg.GREEN}Completed{st.RESET_ALL}\n")


# Begin handling Discord bot stuff
@client.event
async def on_ready():
    print(f"{fg.GREEN}Logged in{st.RESET_ALL} as {client.user}.")
    initialise_onceready()
    await client.change_presence(activity=JukeBot.Config.ACTIVITY_STATUS)
    print(f"\n{fg.GREEN}Bot is ready!{st.RESET_ALL} Command prefix is {fg.GREEN}{JukeBot.Config.COMMAND_PREFIX}{st.RESET_ALL}")
    print(f"Press {fg.YELLOW}Ctrl+C{st.RESET_ALL} to safely shut down JukeBot.\n")


@client.event  # Handles errors in nextcord commands
async def on_command_error(ctx, error):
    if type(error) == nextcord.commands.MissingRequiredArgument:
        await JukeBot.checks.argument_is_missing(ctx)
        return

    if type(error) == nextcord.commands.CheckFailure:
        return  # No need to raise an exception and clog up the user's logfiles.

    if type(error) == commands.CommandNotFound:
        await JukeBot.checks.command_not_found(ctx)
        return

    logging.error("=====================================================================================")
    logging.error("UNHANDLED COMMAND ERROR, PLEASE REPORT TO https://github.com/JukeBot-Org/JukeBot/issues", exc_info=error)
    logging.error("=====================================================================================")
    raise error


def start_bot():
    initialise_preready()
    print(f"\n{fg.YELLOW}Logging in...{st.RESET_ALL}")
    client.run(JukeBot.Config.DISCORD_BOT_TOKEN)  # Hello, world!

    # except Exception as error:  # Handles non-command errors
    #     logging.error("=====================================================================================")
    #     logging.exception("UNHANDLED GENERIC ERROR, PLEASE REPORT TO https://github.com/JukeBot-Org/JukeBot/issues")
    #     logging.error("=====================================================================================")
    #     raise error
