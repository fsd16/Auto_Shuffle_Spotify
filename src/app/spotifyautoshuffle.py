#https://developer.spotify.com/dashboard/8514735c3caf439490cf06059cd0c269/settings

import logging
import os
import random
from pathlib import Path

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler

_dir = Path(__file__).resolve().parent

log_dir = _dir.parent.parent.joinpath('logs', 'schedule.log')

# Create a custom logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(log_dir)
# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
log.addHandler(c_handler)
log.addHandler(f_handler)

load_dotenv()

# Set your Spotify API credentials
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')  # Redirect URI you specified in the Spotify Developer Dashboard

# Define the required scopes
scopes = ['playlist-modify-public', 'playlist-modify-private']

# Initialize the Spotify OAuth client
log.info("Initializng the Spotify API client")
sp = Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scopes, cache_handler=CacheFileHandler(_dir.joinpath('.cache'))))

user_id = sp.me()['id']

# playlists to shuffle
log.info("Requesting user playlists")
playlists = sp.current_user_playlists()

log.info("Shuffling user playlists")
for p in playlists['items']:
    if p['owner']['id'] == user_id:
        # print(f'Name: {p["name"]}, ID: {p["id"]}')

        # Retrieve playlist tracks
        playlist = sp.playlist_tracks(p['id'])

        # # print(json.dumps(playlist, indent=4, sort_keys=True))

        # Extract the track URIs
        track_uris = [track['track']['uri'] for track in playlist['items']]

        # Shuffle the track URIs
        random.shuffle(track_uris)

        # Reorder the playlist with shuffled track URIs
        sp.user_playlist_replace_tracks(sp.me()['id'], p["id"], track_uris)

        log.info(f'{p["name"]} shuffled successfully!')

log.info("Shuffling complete!")