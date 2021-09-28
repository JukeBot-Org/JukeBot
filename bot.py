import nextcord
from nextcord.ext import commands
import json
import config
from sys import platform

from music_player import music_cog

# Explicitly try loading the Opus library if not on Windows.
if platform != "win32":
    print("Need to manually load Opus.")
    import ctypes
    import ctypes.util

    print("\nFinding Opus library...")
    opus_loc = ctypes.util.find_library('opus')
    print(opus_loc)

    print("\nNextcord - Loading Opus...")
    load_opus = nextcord.opus.load_opus(opus_loc)
    print(load_opus)

    print("\nNextcord - Checking if Opus is loaded?")
    opus_loaded = nextcord.opus.is_loaded()
    print(opus_loaded)

    if not opus_loaded:
        print("Opus not loaded! Audio may not work.")
else:
    print("Manually loading Opus not necessary, skipping.")


client = commands.Bot(command_prefix=commands.when_mentioned_or(config.COMMAND_PREFIX))
client.add_cog(music_cog(client))

@client.event
async def on_ready():
    print('Logged in as {0.user}.'.format(client))
    print('Bot is ready! Command prefix is {}'.format(config.COMMAND_PREFIX))
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="time go by"))

if __name__ == '__main__':
    print('\nLogging in...')
    client.run(config.DISCORD_BOT_TOKEN)
