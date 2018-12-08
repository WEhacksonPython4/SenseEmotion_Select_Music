# 事前に、コマンドプロンプトでpip install spotipy
# 参考サイト：
# https://spotipy.readthedocs.io/en/latest/
# https://githubja.com/plamere/spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config

CLIENT_ID = config.CLIENT_ID_SPOTIFY
CLIENT_SECRET = config.CLIENT_SECRET_SPOTIFY
client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# ※Spotifyで曲を再生（playback）できるか？


# サンプルコード1
results = sp.search(q='weezer', limit=20)
for i, t in enumerate(results['tracks']['items']):
    print(' ', i, t['name'])

# サンプルコード2
playlists = sp.user_playlists('spotify')
while playlists:
    for i, playlist in enumerate(playlists['items']):
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
    if playlists['next']:
        playlists = sp.next(playlists)
    else:
        playlists = None

