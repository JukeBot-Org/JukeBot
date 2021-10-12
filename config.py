import json
import os
from datetime import datetime

import colorama
from colorama import Fore as fg
from colorama import Style as st
colorama.init()

conf_file = open("config.json", "r")
config_settings = json.loads(conf_file.read())
exec_time = datetime.now().strftime("%d-%m-%Y_%H:%M:%S")

DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
FFMPEG_PATH       = config_settings["FFMPEG_PATH"]
COMMAND_PREFIX    = config_settings["COMMAND_PREFIX"]
LISTENING_TO      = "{}help".format(COMMAND_PREFIX)

LOG_FILE_DIR      = os.path.join(os.getcwd(), "logs")
LOG_FILE_NAME     = f"jukebot_{exec_time}.log"
LOG_FILE_PATH     = os.path.join(LOG_FILE_DIR, LOG_FILE_NAME)
