import nextcord
from nextcord.ext import commands
from youtube_dl import YoutubeDL
import json
import os
from pathlib import Path
from colorama import Fore, Style
from embed_dialogs import DialogBox
import git

import config

def dbug(foo):
    return "`{}`".format(foo)

class Music_Player(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Determines whether or not the bot is currently playing.
        # If music is already playing and a new play request is received, it will instead be queued.
        self.is_playing = False

        self.music_queue = [] # [song data, voice channel to join when played]
        self.YDL_OPTIONS = {
            "format"     : "bestaudio",
            "noplaylist" : "True"
        }
        self.FFMPEG_OPTIONS = {
            "before_options" : "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options"        : "-vn",
            "executable"     : config.FFMPEG_PATH
        }
        self.vc = "" # Stores the current channel

# ===================== FUNCTIONS ====================== #
    def search_yt(self, item):
        """ Searches YouTube for the requested search term, returns the first result only."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)["entries"][0]
            except Exception:
                print("====================================\n" + Style.RESET_ALL)
                return False
        print("====================================\n" + Style.RESET_ALL)
        print(json.dumps(info, indent=4))
        return { "source"   : info["formats"][0]["url"],
                 "title"    : info["title"],
                 "thumb"    : info["thumbnail"],
                 "duration" : info["duration"]
               }

    async def play_music(self, ctx):
        if len(self.music_queue) > 0: # If there are tracks in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"]

            if self.vc == "": # If not in a voice channel currently...
                print(dbug("Joining VC..."))
                self.vc = await self.music_queue[0]["voice_channel"].connect()
            else:
                print(dbug("Gotta move VCs..."))

            self.music_queue.pop(0)
            self.vc.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False

    def play_next(self, ctx):
        if len(self.music_queue) > 0: # If there's music waiting in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"] # ...get the first URL...
            self.music_queue.pop(0)                                # ...remove the first element from the queue...

            # ...then play the music in the current VC!
            # Once the music is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.vc.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next(ctx))
        else:
            self.is_playing = False # Stop playing music.


# ====================== COMMANDS ====================== #
    @commands.command()
    async def isplaying(self, ctx, *args):
        """Debug command"""
        await ctx.send(embed=DialogBox("Debug", "Debug", "self.is_playing = `{}`".format(self.is_playing)))

    @commands.command()
    async def play(self, ctx, *args):
        """Plays a song in the voice channel that you're currently in.
        Takes YouTube links, search terms, and Spotify links (TODO)
        """
        query = " ".join(args)

        if ctx.author.voice is None:
            await ctx.send(embed=DialogBox("Warn", "Hang on!",
                                           "Connect to a voice channel first, _then_ issue the command."))
            return
        voice_channel = ctx.author.voice.channel

        song_data = self.search_yt(query)
        if song_data == False:
            await ctx.send(".")
            await ctx.send(embed=DialogBox("Error", "Unable to play song",
                                           "Incorrect video format or link type."))
            return

        self.music_queue.append({
            "song_data"     : song_data,
            "voice_channel" : voice_channel
        })

        if self.is_playing == False:
            await ctx.message.delete()
            reply = DialogBox("Playing", "Now playing: {}".format(song_data['title']))
            reply.set_image(url=song_data['thumb'])
            reply.add_field(name='Duration' , value=song_data["duration"], inline=True)
            await ctx.send(embed=reply)

            await self.play_music(ctx)

        else:
            await ctx.message.delete()
            reply = DialogBox("Queued", "Adding to queue: {}".format(song_data['title']))
            reply.set_image(url=song_data['thumb'])
            reply.add_field(name='Duration' , value=song_data["duration"], inline=True)
            await ctx.send(embed=reply)

    @commands.command()
    async def about(self, ctx):
        repo      = git.Repo(search_parent_directories=True)
        reply = DialogBox("Version", "Thank you for using JukeBot!",
        """**JukeBot** is a self-hostable music streaming bot that runs on spite, a love for freedom, and Python 3.\n
        You can find more information on the project, as well as the source code to host your own instance of JukeBot, at **https://squigjess.github.io/JukeBot**""")
        reply.set_image(url="https://media.discordapp.net/attachments/891977633275969537/894946455721218068/jukebot.png")
        reply.set_footer(text="JukeBot v.{version} ({branch} branch)".format(version=repo.head.object.hexsha[0:7],
                                                                             branch=repo.head.ref))
        await ctx.send(embed=reply)
