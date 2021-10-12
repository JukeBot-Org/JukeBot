import json
import colorama
from colorama import Fore as fg
from colorama import Style as st
colorama.init()

try:
    conf_file = open("config.json", "r")
    config_settings = json.loads(conf_file.read())
    DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
    FFMPEG_PATH       = config_settings["FFMPEG_PATH"]
    COMMAND_PREFIX    = config_settings["COMMAND_PREFIX"]
    LISTENING_TO      = "{}help".format(COMMAND_PREFIX)
except json.decoder.JSONDecodeError as e:
    print(f"{fg.RED}FATAL ERROR:{st.RESET_ALL} config.json looks to be incorrectly formatted: {e.msg}")
    print("Correct any issues and try running JukeBot again.")
    exit()
