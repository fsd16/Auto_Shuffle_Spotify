#https://developer.spotify.com/dashboard/8514735c3caf439490cf06059cd0c269/settings

import logging
import os
import random
import json
from pathlib import Path

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler

def get_playlist_tracks(playlist_id, *args, **kwargs):
    results = sp.playlist_tracks(playlist_id, *args, **kwargs)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

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
playlists = sp.current_user_playlists()['items']

log.info("Shuffling user playlists")
for playlist in playlists:
    if playlist['owner']['id'] == user_id:

        # Retrieve playlist tracks
        results = sp.playlist_items(playlist['id'])
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        # Extract the track URIs
        track_uris = [track['track']['uri'] for track in tracks]

        # Shuffle the track URIs
        random.shuffle(track_uris)

        # Replace the playlist items with shuffled items
        sp.playlist_replace_items(playlist['id'], [])
        batch_size = 100
        track_batches = [track_uris[i:i+batch_size] for i in range(0, len(track_uris), batch_size)]
        for batch in track_batches:
            sp.playlist_add_items(playlist['id'], batch)

        log.info(f'{playlist["name"]} shuffled successfully!')

log.info("Shuffling complete!")