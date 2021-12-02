"""Loads and defines global constants
"""
import toml
import os
from datetime import datetime
from dataclasses import dataclass
from nextcord import Activity, ActivityType

with open("JukeBot.config", "r") as conf_file:
    conf_file = toml.loads(conf_file.read())


@dataclass
class Config:
    # App information
    RELEASE_VER = "0.3.0.dev2"
    EXEC_TIME = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Bot config
    DISCORD_BOT_TOKEN = conf_file["DISCORD_BOT_TOKEN"]
    FFMPEG_PATH = conf_file["FFMPEG_PATH"]
    COMMAND_PREFIX = conf_file["COMMAND_PREFIX"]
    ACTIVITY_STATUS = Activity(type=ActivityType.listening,
                               name="{}help".format(COMMAND_PREFIX))
    MAX_IDLE_TIME = conf_file["MAX_IDLE_TIME"]

    # Logging
    LOG_FILE_DIR = os.path.join(os.getcwd(), "logs")
    LOG_FILE_NAME = f"jukebot_{EXEC_TIME}.log"
    LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)

    # Spotify integration
    SPOTIFY_ENABLED = False
    SPOTIPY_CLIENT_ID = ""
    SPOTIPY_CLIENT_SECRET = ""
    if(conf_file["SPOTIPY_CLIENT_ID"] != "" and conf_file["SPOTIPY_CLIENT_SECRET"] != ""):
        SPOTIFY_ENABLED = True
        SPOTIPY_CLIENT_ID = conf_file["SPOTIPY_CLIENT_ID"]
        SPOTIPY_CLIENT_SECRET = conf_file["SPOTIPY_CLIENT_SECRET"]
