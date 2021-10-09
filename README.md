### Disclaimer
**This code is provided for educational purposes only and is not to be used for any purpose that would infringe on the policies or terms of service of any party.**

------------------------

# JukeBot
A self-hosted audio streaming bot for Discord. Currently supports YouTube, with plans to support local file streaming eventually.

# Installation

## 1. Install Python dependencies
    python3 -m venv venv
    source venv/bin/activate   # For macOS/Linux
    venv/Scripts/activate.bat  # For Windows
    pip install -r requirements.txt

## 2. Set up `config.py`
Rename `config.EXAMPLES.py` to `config.py` and update the FFmpeg path and your Discord bot's token.

## 3. Install FFmpeg
* Download the FFmpeg binaries for your system from [the official ffmpeg.org website](https://ffmpeg.org/download.html)
* Place them somewhere accessible on your machine.
* Update `FFMPEG_PATH` in `config.py`.

## 4. Set up a Discord application and bot
I'm not gonna go into too much detail on this, but create a bot, add it to your server, then put the bot's token in `DISCORD_BOT_TOKEN` in `config.py`.

# To do
* Implement Invite Generator-style error handling.
* Have JukeBot auto-disconnect (maybe after a delay?) when the queue is exhausted.
* Move config to .json in anticipation of exe distribution
* ~~Add a way to clear the queue.~~
* ~~Function-ify redundant embed/dialog code in `!play`.~~
* ~~Work on a nicer-looking `!help` command.~~
* ~~Add a pretty `!queue` command.~~
* ~~Set up GitHub Pages website for JukeBot.~~
* ~~Re-implement `!skip`.~~
* Implement Spotify link recognition and translation (not sure if this is possible with a self-hosted set-up)
