#https://developer.spotify.com/dashboard/8514735c3caf439490cf06059cd0c269/settings

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import random

# Set your Spotify API credentials
***REMOVED***
***REMOVED***
redirect_uri = 'http://localhost:8080'  # Redirect URI you specified in the Spotify Developer Dashboard

# Define the required scopes
scopes = ['playlist-modify-public', 'playlist-modify-private']

# Initialize the Spotify OAuth client
sp = Spotify(auth_manager=SpotifyOAuth(client_id, client_secret, redirect_uri, scope=scopes))

user_id = sp.me()['id']

# playlists to shuffle
playlists = sp.current_user_playlists()

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

        print(f'{p["name"]} shuffled successfully!')            