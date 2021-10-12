import nextcord as discord
from nextcord.ext import commands
import sys
import colorama
from colorama import Fore as fg
from colorama import Style as st
import logging

import config
from embed_dialogs import JukeBot_Bluegreen
from music_commands import Music
from misc_commands import Other, ImprovedHelp

logging.basicConfig(filename=config.LOG_FILE_PATH, level=logging.WARNING, format="%(asctime)s %(levelname)s:%(message)s")
client = commands.Bot(command_prefix=config.COMMAND_PREFIX, help_command=ImprovedHelp())

# Explicitly try loading the Opus library if not on Windows.
if sys.platform == "win32":
    print(f"{fg.YELLOW}Manually loading Opus not necessary, skipping.{st.RESET_ALL}")
else:
    print(f"{fg.YELLOW}Need to manually load Opus.{st.RESET_ALL}")
    import ctypes
    import ctypes.util
    print("Finding Opus library...")
    opus_loc = ctypes.util.find_library('opus')
    print("Loading Opus...")
    load_opus = discord.opus.load_opus(opus_loc)
    print("Checking if Opus is loaded...")
    if discord.opus.is_loaded():
        print(f"{fg.GREEN}Opus module loaded successfully.{st.RESET_ALL}")
    else:
        print(f"{fg.RED}Opus not loaded! Audio may not work.{st.RESET_ALL}")

@client.event
async def on_ready():
    print(f"{fg.GREEN}Logged in{st.RESET_ALL} as {client.user}.")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=config.LISTENING_TO))
    print(f"{fg.GREEN}Bot is ready!{st.RESET_ALL} Command prefix is {fg.GREEN}{config.COMMAND_PREFIX}{st.RESET_ALL}\n")
    print(f"Press {fg.YELLOW}Ctrl+C{st.RESET_ALL} to safely shut down JukeBot.\n")

if __name__ == '__main__':
    try:
        colorama.init()
        client.add_cog(Music(client))
        client.add_cog(Other(client))

        print(f"\n{fg.YELLOW}Logging in...{st.RESET_ALL}")
        client.run(config.DISCORD_BOT_TOKEN)
    except:
        logging.exception('ERROR, PLEASE REPORT TO https://github.com/squigjess/JukeBot/issues')
        raise
