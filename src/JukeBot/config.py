"""Reads JukeBot.config and uses the values within it to define global
variables.
"""
import toml
import os
from datetime import datetime
from JukeBot.utils import embed_dialogs

with open("JukeBot.config", "r") as conf_file:
    config_settings = toml.loads(conf_file.read())
    exec_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

    # Bot config
    RELEASE_VER = "0.3.0 testing"
    DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
    FFMPEG_PATH = config_settings["FFMPEG_PATH"]
    COMMAND_PREFIX = config_settings["COMMAND_PREFIX"]
    LISTENING_TO = "{}help".format(COMMAND_PREFIX)
    MAX_IDLE_TIME = config_settings["MAX_IDLE_TIME"]
    embed_dialogs.version = RELEASE_VER
    VERSION_INFO_IN_FOOTER = False

    # Logging
    LOG_FILE_DIR = os.path.join(os.getcwd(), "logs")
    LOG_FILE_NAME = f"jukebot_{exec_time}.log"
    LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)

    # Spotify integration
    SPOTIFY_ENABLED = False
    if(config_settings["SPOTIPY_CLIENT_ID"] != "" and
       config_settings["SPOTIPY_CLIENT_SECRET"] != ""):
        print("Spotify integration enabled.\n")
        SPOTIFY_ENABLED = True
    SPOTIPY_CLIENT_ID = config_settings["SPOTIPY_CLIENT_ID"]
    SPOTIPY_CLIENT_SECRET = config_settings["SPOTIPY_CLIENT_SECRET"]
