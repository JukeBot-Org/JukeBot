# JukeBot
A self-hosted audio streaming bot for Discord. Currently supports YouTube, with plans to support local file streaming eventually.

## Installation

### 1. Install Python dependencies
    virtualenv venv
    source venv/bin/activate   # For macOS/Linux
    venv/Scripts/activate.bat  # For Windows
    pip install -r requirements.txt

### 2. Set up `config.py`
Rename `config.EXAMPLES.py` to `config.py` and update the FFmpeg path and your Discord bot's token.

### 3. Install FFmpeg
* Download the FFmpeg binaries for your system from [the official ffmpeg.org website](https://ffmpeg.org/download.html)
* Place them somewhere accessible on your machine.
* Update `FFMPEG_PATH` in `config.py`.

### 4. Set up a Discord application ands bot
I'm not gonna go into too much detail on this, but create a bot, add it to your server, then put the bot's token in `DISCORD_BOT_TOKEN` in `config.py`.
