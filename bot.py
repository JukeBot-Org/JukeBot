import nextcord
from nextcord.ext import commands
import json
import config
from sys import platform
import colorama
from colorama import Fore, Style

from music_player import Music_Player

colorama.init()

# Explicitly try loading the Opus library if not on Windows.
if platform == "win32":
    print(Fore.YELLOW + "Manually loading Opus not necessary, skipping." + Style.RESET_ALL)
else:
    print(Fore.YELLOW + "Need to manually load Opus." + Style.RESET_ALL)
    import ctypes
    import ctypes.util

    print("Finding Opus library...")
    opus_loc = ctypes.util.find_library('opus')
    print("Loading Opus...")
    load_opus = nextcord.opus.load_opus(opus_loc)
    print("Checking if Opus is loaded...")
    if nextcord.opus.is_loaded():
        print(Fore.GREEN + "Opus module is loaded." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Opus not loaded! Audio may not work." + Style.RESET_ALL)

client = commands.Bot(command_prefix=commands.when_mentioned_or(config.COMMAND_PREFIX))
client.add_cog(Music_Player(client))

@client.event
async def on_ready():
    print(Fore.GREEN + 'Logged in ' + Style.RESET_ALL + 'as {0.user}.'.format(client) )
    print(Fore.GREEN + 'Bot is ready! ' + Style.RESET_ALL + 'Command prefix is {}\n'.format(config.COMMAND_PREFIX))
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=config.LISTENING_TO))

if __name__ == '__main__':
    print(Fore.YELLOW + '\nLogging in...' + Style.RESET_ALL)
    client.run(config.DISCORD_BOT_TOKEN)
