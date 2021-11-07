"""Reads JukeBot.config and uses the values within it to define global
variables.
"""
import toml
import os
from datetime import datetime

conf_file = open("JukeBot.config", "r")
config_settings = toml.loads(conf_file.read())
exec_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

RELEASE_VER = "0.0.0"
DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
FFMPEG_PATH = config_settings["FFMPEG_PATH"]
COMMAND_PREFIX = config_settings["COMMAND_PREFIX"]
LISTENING_TO = "{}help".format(COMMAND_PREFIX)
MAX_IDLE_TIME = config_settings["MAX_IDLE_TIME"]

LOG_FILE_DIR = os.path.join(os.getcwd(), "logs")
LOG_FILE_NAME = f"jukebot_{exec_time}.log"
LOG_FILE_PATH = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
conf_file.close()
