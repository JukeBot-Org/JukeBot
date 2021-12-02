"""Handles the various processes between the user invoking !play and JukeBot
constructing a JukeBot.Track object to add to the queue."""

import JukeBot
from JukeBot.Utils.embed_dialogs import dialogBox
from colorama import Fore, Style
import youtube_dl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=JukeBot.Config.SPOTIPY_CLIENT_ID,
                                                           client_secret=JukeBot.Config.SPOTIPY_CLIENT_SECRET))


class _Searcher:
    def __init__(self):
        self.YDL_OPTIONS = {"format": "bestaudio",
                            "noplaylist": "True"}
        self.spotify_matches = ["https://open.spotify.", "http://open.spotify."]
        self.youtube_matches = ["https://youtube.", "https://youtu.be",
                                "http://youtube.", "http://youtu.be"]

        self.pl_dt = lambda cnt, max: dialogBox("Loading", "Playlist detected! This may take a while, please be patient...",
                                                f"Track {cnt} out of {max} loaded...")

    def link_type(self, search_query: str):
        """Takes a web link/search term and lets us know whether its for a
        track on YouTube, a track/playlist/album on Spotify, or a search
        query to be plugged into YouTube.
        """
        service = None
        media_type = None

        for spotify_match in self.spotify_matches:
            if search_query.startswith(spotify_match):
                service = "spotify"
                media_type = search_query.split("?")[0].split("/")[3:][0]  # fucked
                break

        for youtube_match in self.youtube_matches:
            if search_query.startswith(youtube_match):
                service = "youtube"
                media_type = "track"
                break

        # If no matches, the user probably entered a search query.
        # We'll try to search it on YouTube. If that fails, an error will
        # still be thrown regardless.
        if service is None and media_type is None:
            service = "youtube"
            media_type = "track"

        return [service, media_type]

    def translate_youtube(self, item: str):
        """Searches YouTube for the requested search term or URL, returns a
        dict of track info for the first result only. Returns False on an
        error, otherwise a JukeBot.Track instance if successful."""

        print(Fore.YELLOW + "======== YouTube Downloader ========")
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:  # If we get a DownloadError while trying to fetch the YouTube data, it's probably a stream.
                ydl_results = ydl.extract_info(f"ytsearch:{item}", download=False)["entries"]
            except Exception as e:
                print(type(e))
                return False
            if len(ydl_results) == 0:  # The list above will be empty if there were any issues.
                return False
            ytdl_data = ydl_results[0]
        print("====================================\n" + Style.RESET_ALL)

        return ytdl_data

    def translate_spotify(self, spotify_url):
        track_info = sp.track(spotify_url)
        return track_info

    async def find(self, search_query, ctx, loading_msg):
        """The main entrypoint. Takes the user's search query and converts
        it into a list of playable JukeBot.Track objects.
        """
        track_list = []
        playlist_info = {"type": None, "name": None, "thumb": None}
        # STEP 1: Figure out which service this is for and whether this is a
        # playlist or a single track (albums are playlists to JukeBot's
        # understanding)
        service, media_type = self.link_type(search_query)
        playlist_info = {"type": media_type, "name": None, "thumb": None}

        # STEP 2.1: If this was a YouTube link, simply find the track on
        # YouTube.
        if service == "youtube" and media_type == "track":
            # Get the track straight from YouTube, put the info in a Track obj
            youtube_track_info = self.translate_youtube(search_query)
            if youtube_track_info is False:
                return []
            track_list.append(JukeBot.Track(source=youtube_track_info["formats"][0]["url"],
                                            title=youtube_track_info["title"],
                                            thumb=youtube_track_info["thumbnails"][2]["url"],
                                            web_url=youtube_track_info["webpage_url"],
                                            duration=youtube_track_info["duration"],
                                            ctx=ctx))

        # STEP 2.2: If this was a Spotify link...
        if service == "spotify":
            all_tracks = []
            # Get the Spotify API data for all the tracks requested and
            # put 'em into all_tracks.
            if media_type == "track":
                # Get the track info from Spotify, add it to the track list
                # for this query.
                all_tracks.append(self.translate_spotify(search_query))

            if media_type == "playlist":
                try:
                    api_result = sp.playlist(search_query)
                except spotipy.exceptions.SpotifyException:
                    return []
                playlist_info["name"] = api_result["name"]
                playlist_info["thumb"] = api_result["images"][0]["url"]
                for track_info in api_result["tracks"]["items"]:
                    all_tracks.append(track_info["track"])

            if media_type == "album":
                all_tracks = []
                try:
                    api_result = sp.album(search_query)
                except spotipy.exceptions.SpotifyException:
                    return []
                playlist_info["name"] = api_result["name"]
                playlist_info["thumb"] = api_result["images"][1]["url"]
                for track_info in api_result["tracks"]["items"]:
                    track_info["album"] = {}
                    track_info["album"]["images"] = api_result["images"]
                    all_tracks.append(track_info)

            # For each track requested, search for it on YouTube and add it
            # to the track list.
            count = 0
            if len(all_tracks) >= 2:
                await loading_msg.edit(embed=self.pl_dt(count, len(all_tracks)))
            for track in all_tracks:
                # Turn the link into a search query that can be plugged
                # into YouTube.
                artists = "".join(f"{a['name']} " for a in track["artists"])[:-1]
                title = track["name"]

                searchable = f"\"{artists}\" \"{title}\""
                # Find the track on YouTube and create a new JukeBot.Track
                # object, only this time we'll use the Spotify album art
                # and web URL.
                youtube_track_info = self.translate_youtube(searchable)
                if youtube_track_info is False:
                    return []
                track_list.append(JukeBot.Track(source=youtube_track_info["formats"][0]["url"],
                                                title=youtube_track_info["title"],
                                                thumb=track["album"]["images"][1]["url"],
                                                web_url=track["external_urls"]["spotify"],
                                                duration=youtube_track_info["duration"],
                                                ctx=ctx))
                count += 1
                if len(all_tracks) >= 2:
                    await loading_msg.edit(embed=self.pl_dt(count, len(all_tracks)))

        return [track_list, playlist_info]


TrackSearch = _Searcher()
