import json
conf_file = open("config.json", "r")
config_settings = json.loads(conf_file.read())
DISCORD_BOT_TOKEN = config_settings["DISCORD_BOT_TOKEN"]
FFMPEG_PATH       = config_settings["FFMPEG_PATH"]
COMMAND_PREFIX    = config_settings["COMMAND_PREFIX"]
LISTENING_TO      = "{}help".format(COMMAND_PREFIX)
