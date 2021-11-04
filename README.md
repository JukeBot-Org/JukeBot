### Disclaimer
**This code is provided for educational purposes only and is not to be used for any purpose that would infringe on the policies or terms of service of any party.**

------------------------

[![Powered by Nextcord](https://custom-icon-badges.herokuapp.com/badge/-Powered%20by%20Nextcord-0d1620?logo=nextcord)](https://github.com/nextcord/nextcord "Powered by Nextcord Python API Wrapper") ![Scrutinizer code quality (GitHub)](https://img.shields.io/scrutinizer/quality/g/squigjess/JukeBot/testing) ![Scrutinizer build status](https://img.shields.io/scrutinizer/build/g/squigjess/JukeBot/testing)

# JukeBot

**http://squigjess.github.io/JukeBot/**

A self-hosted audio streaming bot for Discord. Currently supports YouTube, with plans to support other services and local file streaming eventually.

While it currently works, JukeBot is still under development. A lot of the bugs are still being found and worked on. As a result, the current version you see here in the `live` branch is technically a testing version that happens to be deployed to a few private Discord servers for testing purposes.

If you would like to run JukeBot and report on your bugs and issues, I would be forever grateful.

# Installation

## 1. Install Python dependencies with `pip`
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 2. Install FFmpeg
* Download the FFmpeg binaries for your system from [the official ffmpeg.org website](https://ffmpeg.org/download.html)
* Place them somewhere accessible on your machine.
* Update `FFMPEG_PATH` in `config.py`.

## 3. Set up a Discord application and bot
I'm not gonna go into too much detail on this, but create a bot, add it to your server, then put the bot's token in `DISCORD_BOT_TOKEN` in `config.py`.

## 4. Set up `config.py`
* Rename `JukeBot.EXAMPLES.config` to `JukeBot.config`
* Update the config file with the FFmpeg path and your Discord bot's token.

-------

# To do
* Behind the scenes stuff
  * Move long strings to .txt files
* Documentation
  * Update README and Quickstart once build process is sorted out
    * [include this warning](https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d#gistcomment-3311754)
