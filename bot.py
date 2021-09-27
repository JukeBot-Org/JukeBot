import nextcord
from nextcord.ext import commands
import json
import config

from music_player import music_cog

client = commands.Bot(command_prefix=commands.when_mentioned_or('!'))
client.add_cog(music_cog(client))

@client.event
async def on_ready():
	print('Logged in as {0.user}.'.format(client))
	await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name=config.LISTENING_TO))

#============================= COMMANDS =============================#

if __name__ == '__main__':
    print('Logging in...')
    client.run(config.DISCORD_BOT_TOKEN)
