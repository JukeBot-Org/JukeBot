import json
from sys import exit
from datetime import datetime

import colorama
from colorama import Fore as fg
from colorama import Style as st
colorama.init()

conf_file = open("config.json", "r")
config_settings = json.loads(conf_file.read())
exec_time = datetime.now().strftime("%d-%m-%&_%H:%M:%S")

DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
FFMPEG_PATH       = config_settings["FFMPEG_PATH"]
COMMAND_PREFIX    = config_settings["COMMAND_PREFIX"]
LISTENING_TO      = "{}help".format(COMMAND_PREFIX)
LOG_FILE_PATH     = f"jukebot-{exec_time}.log"
