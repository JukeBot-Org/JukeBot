import nextcord
from nextcord.ext import commands
import json
import config
from sys import platform

from music_player import music_cog

# Explicitly try loading the Opus library if not on Windows.
if platform != "win32":
    import ctypes
    import ctypes.util

    print("Finding Opus library...")
    opus_loc = ctypes.util.find_library('opus')
    print(opus_loc)

    print("Nextcord - Loading Opus...:")
    load_opus = nextcord.opus.load_opus(a)
    print(load_opus)

    print("Nextcord - Checking if Opus is loaded?")
    opus_loaded = nextcord.opus.is_loaded()
    print(opus_loaded)

    if not opus_loaded:
        print("Opus not loaded! Audio may not work.")


client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))
client.add_cog(music_cog(client))

@client.event
async def on_ready():
    print('Logged in as {0.user}.'.format(client))
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="time go by"))

if __name__ == '__main__':
    print('Logging in...')
    client.run(config.DISCORD_BOT_TOKEN)
