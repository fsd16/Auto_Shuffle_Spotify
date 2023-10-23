"""
Spotify Playlist Shuffler and Backup Script

This script retrieves playlists for a user from their Spotify account, shuffles the tracks within each playlist, overwrites the shuffled playlists back to Spotify, and creates backups of the original playlists in JSON format.

Author: Finn Drabsch
Date: 19/08/2023
GitHub: https://github.com/fsd16/Auto_Shuffle_Spotify

Usage:
1. Ensure you have registered your application on the Spotify Developer Dashboard to obtain client credentials.
2. Create a .env file in the script directory containing:

    SPOTIPY_CLIENT_ID = <your_client_id>
    SPOTIPY_CLIENT_SECRET = <your_client_secret>
    SPOTIPY_REDIRECT_URI = <your_redirect_uri>

3. Run the script to shuffle playlists and create backups.

Note:
- This script requires the 'spotipy' and 'python-dotenv' packages, which can be installed using 'pip install spotipy python-dotenv'.

"""

import logging
import os
from datetime import datetime
from json import dumps
from pathlib import Path
from random import shuffle
from zipfile import ZIP_LZMA, ZipFile

from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

# Generate the current timestamp
_timestamp = datetime.now().astimezone().isoformat(timespec='seconds')

# Get the script directory
_dir = Path(__file__).resolve().parent

# Initilize logging and backup directories
log_dir = _dir.parent.parent.joinpath('logs')
bkup_dir = _dir.parent.parent.joinpath('backups')

log_filename = log_dir.joinpath('autoshuffle.log')

# Create custom loggers
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler(log_filename)
# c_handler.setLevel(logging.INFO)
# f_handler.setLevel(logging.INFO)

# Create formatters and add to handlers
c_format = logging.Formatter('%(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
log.addHandler(c_handler)
log.addHandler(f_handler)

# Load environment variables from the local .env
load_dotenv()

# Initilize Spotify API credentials
client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')  # Redirect URI you specified in the Spotify Developer Dashboard

# Define the required scopes
scopes = ['playlist-modify-public', 'playlist-modify-private']

# Initialize the Spotify API client
log.info("Initializng the Spotify API client")
sp = Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scopes, cache_handler=CacheFileHandler(_dir.joinpath('.cache'))))

# Initialize the user id
user_id = sp.me()['id']

# Get all user playlists
log.info("Requesting user playlists")
playlists = sp.current_user_playlists()['items']

# Initilize list to store playlist backups
backup = list()

# Store original playlists for backup, shuffle each playlist, and overwrite shuffled playlists to spotify
log.info("Shuffling user playlists")
for playlist in playlists:
    # Only shuffle playlist owned by the user
    if playlist['owner']['id'] == user_id:

        # Retrieve playlist tracks (have to do this iteratively due to limit of 100 items)
        results = sp.playlist_items(playlist['id'])
        tracks = results['items']
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        # Store tracks for back up
        playlist['tracks'].update({'items': tracks})
        backup.append(playlist)

        # Extract the track URIs
        track_uris = [track['track']['uri'] for track in tracks]

        # Shuffle the track URIs
        shuffle(track_uris)

        # Overwrite the original Spotify playlist with the shuffled list (have to do this iteratively due to limit of 100 items)
        sp.playlist_replace_items(playlist['id'], [])
        batch_size = 100
        track_batches = [track_uris[i:i+batch_size] for i in range(0, len(track_uris), batch_size)]
        for batch in track_batches:
            sp.playlist_add_items(playlist['id'], batch)

        log.info(f'{playlist["name"]} shuffled successfully!')

log.info("Shuffling complete!")

# Back up the original playlists
log.info("Backing up the original playlists")
bkup_filename_json = Path(f'playlists_{_timestamp}.json')
bkup_filename_zip = bkup_dir.joinpath(bkup_filename_json.with_suffix('.zip'))
with ZipFile(bkup_filename_zip, 'w', ZIP_LZMA) as zipf:
    zipf.writestr(str(bkup_filename_json), dumps(backup, indent=4))

log.info("Back up complete!")