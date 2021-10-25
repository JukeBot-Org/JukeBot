### Disclaimer
**This code is provided for educational purposes only and is not to be used for any purpose that would infringe on the policies or terms of service of any party.**

------------------------

[![Powered by Nextcord](https://custom-icon-badges.herokuapp.com/badge/-Powered%20by%20Nextcord-0d1620?logo=nextcord)](https://github.com/nextcord/nextcord "Powered by Nextcord Python API Wrapper") ![Python version](https://img.shields.io/github/pipenv/locked/python-version/squigjess/JukeBot/testing) ![Scrutinizer code quality (GitHub)](https://img.shields.io/scrutinizer/quality/g/squigjess/JukeBot/testing) ![Scrutinizer build status](https://img.shields.io/scrutinizer/build/g/squigjess/JukeBot/testing)

# JukeBot

**http://squigjess.github.io/JukeBot/**

A self-hosted audio streaming bot for Discord. Currently supports YouTube, with plans to support other services and local file streaming eventually.

While it currently works, JukeBot is still under development. A lot of the bugs are still being found and worked on. As a result, the current version you see here in the `live` branch is technically a testing version that happens to be deployed to a few private Discord servers for testing purposes.

If you would like to run JukeBot and report on your bugs and issues, I would be forever grateful.

# Installation

## 1. Install Python dependencies with `pipenv`
    pipenv shell
    pipenv install
    pipenv install --dev # for build dependencies

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
* Bugs
  * N/A
* Features
  * playing local files
  * Saving queues
* Behind the scenes stuff
  * Any better way to write help w/ nextcord?
  * ignore_extra?
  * Write tests
  * Test multi-server capabilities
  * Move queue from a list to a JukeBot.queue.Queue object.
  * Move back to pretty-help now that I've ported it to Nextcord.
  * [Move to discord.py's inherent checks system](https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html?highlight=on_command_error#checks)
  * https://pyinstaller.readthedocs.io/en/stable/operating-mode.html#hiding-the-source-code
  * https://pyinstaller.readthedocs.io/en/stable/usage.html#cmdoption-i
* Documentation
  * Update README and Quickstart once build process is sorted out
    * [include this warning](https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d#gistcomment-3311754)
* Maybes
  * Implement Spotify link recognition and translation (not sure if this is possible with a self-hosted set-up)
<!--
* `ctx.reply()` over `ctx.reply()`
* Add `!resume`, `!pause`, and `!stop` commands
* Move from JSON to TOML for user config
* Send a message to the last text channel when JukeBot disconnects.
* [Have JukeBot auto-disconnect (maybe after a delay?) when the queue is exhausted.](https://www.py4u.net/discuss/262449)
* [Implement proper error handling](https://discordpy.readthedocs.io/en/stable/ext/commands/commands.html?highlight=on_command_error#error-handling)
* Fix exception when invoking `!nowplaying` with an empty queue
* stopwatch (under `!nowplaying`)
* Find out why compiled version doesn't launch a terminal window on Linux.
* Implement the ability to remove a single track from the queue in !clear
* Track/queue data refactor
* Make "queued" msg titles link to the OG video
* Logfile
* Update docstrings
* work on build script
* Move config to .json in anticipation of exe distribution
* Add a way to clear the queue.
* Function-ify redundant embed/dialog code in `!play`.
* Work on a nicer-looking `!help` command.
* Add a pretty `!queue` command.
* Set up GitHub Pages website for JukeBot.
* Re-implement `!skip`.
* PySimpleGUI
-->
