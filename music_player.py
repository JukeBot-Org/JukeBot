import nextcord
from nextcord.ext import commands
from youtube_dl import YoutubeDL
import json
import os
from pathlib import Path
from colorama import Fore, Style
from embed_dialogs import DialogBox

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
        return { "source"   : info["formats"][0]["url"],
                 "title"    : info["title"],
                 "thumb"    : info["thumbnail"]
               }

    async def play_music(self, ctx):
        if len(self.music_queue) > 0: # If there are tracks in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"]

            # Try to connect to the VC if not connected
            #await ctx.send("**{}** will be played right now!".format(self.music_queue[0]["song_data"]["title"])) #EMBEDDIALOGSSSSS
            print(dbug(self.vc))

            if self.vc == "": # If not in a voice channel currently...
                print(dbug("Joining VC..."))
                self.vc = await self.music_queue[0]["voice_channel"].connect()
            else:
                print(dbug("Gotta move VCs..."))

            self.music_queue.pop(0)
            self.vc.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False

    def play_next(self):
        if len(self.music_queue) > 0: # If there's music waiting in the queue...
            self.is_playing = True
            media_url = self.music_queue[0]["song_data"]["source"] # ...get the first URL...
            self.music_queue.pop(0)                                # ...remove the first element from the queue...

            # ...then play the music in the current VC!
            # Once the music is finished playing, repeat from the start.
            # Loop until the queue is empty, at which point...
            self.vc.play(nextcord.FFmpegPCMAudio(media_url, **self.FFMPEG_OPTIONS),
                         after=lambda e: self.play_next())
        else:
            self.is_playing = False # Stop playing music.

# ====================== COMMANDS ====================== #
    @commands.command()
    async def debug_yt(self, ctx, *args):
        """Debug command"""
        query = self.search_yt(" ".join(args))
        await ctx.send(embed=DialogBox("Debug", "Debug", "`{}`".format(query))) #EMBEDDIALOGSSSSS

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
            await ctx.send(".") #EMBEDDIALOGSSSSS
            await ctx.send(embed=DialogBox("Error", "Unable to play song",
                                           "Incorrect video format or link type."))
            return

        self.music_queue.append({
            "song_data"     : song_data,
            "voice_channel" : voice_channel
        })

        if self.is_playing == False:
            await self.play_music(ctx)
        else:
            await ctx.send(embed=DialogBox("Queued", "Adding to queue...",
                                           "LOREM MY FAT IPSUM YOU DUMB BITCH."))

    @commands.command()
    async def queue(self, ctx):
        """Shows the queue of songs waiting to be played."""
        queue = []
        for i in range(0, len(self.music_queue)):
            queue.append(self.music_queue[i]["song_data"])

        if queue != []:
            print(json.dumps(queue, indent=4))
        else:
            print("Nothing queued up at the moment!")
