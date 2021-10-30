from youtube_dl import YoutubeDL
import json

YDL_OPTIONS = {"format": "bestaudio",
               "noplaylist": "True"}

with YoutubeDL(YDL_OPTIONS) as ydl:
    ydl_results = ydl.extract_info(f"ytsearch:tom scott disintegrates xnopyt", download=False)

print(json.dumps(ydl_results, indent=4))