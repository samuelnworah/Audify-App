from flask import Flask, redirect, request, url_for, session, render_template
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import logging
from datetime import datetime, timedelta
import calendar

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Spotify API credentials (replace with your actual credentials)
SPOTIPY_CLIENT_ID = 'ad274f1907e7485e826c2979ca114830'
SPOTIPY_CLIENT_SECRET = 'da13ee6f543645e8867ea7d28399c1cf'
SPOTIPY_REDIRECT_URI = 'https://audi-fy-67176c9dbd0e.herokuapp.com/callback'


# Spotify OAuth setup
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope='user-top-read playlist-modify-public user-read-recently-played')

@app.route('/')
def home():
    auth_url = sp_oauth.get_authorize_url()
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    session.clear()
    code = request.args.get('code')
    
    if code:
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info
        return redirect('/top-tracks')
    
    return redirect('/')

@app.route('/top-tracks')
def top_tracks():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])


    # Fetch top data for various time ranges
    top_tracks_short_term = sp.current_user_top_tracks(limit=50, time_range='short_term')
    top_artists_short_term = sp.current_user_top_artists(limit=50, time_range='short_term')
    top_tracks_medium_term = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    top_artists_medium_term = sp.current_user_top_artists(limit=50, time_range='medium_term')
    top_tracks_long_term = sp.current_user_top_tracks(limit=50, time_range='long_term')
    top_artists_long_term = sp.current_user_top_artists(limit=50, time_range='long_term')
    featured_playlists = sp.featured_playlists(limit=10)
    


    # Prepare data for display
    track_data_short_term = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'album': track['album']['name'], 'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None} for track in top_tracks_short_term['items']]
    artist_data_short_term = [{'name': artist['name'], 'image_url': artist['images'][0]['url'] if artist['images'] else None} for artist in top_artists_short_term['items']]
    track_data_medium_term = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'album': track['album']['name'], 'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None} for track in top_tracks_medium_term['items']]
    artist_data_medium_term = [{'name': artist['name'], 'image_url': artist['images'][0]['url'] if artist['images'] else None} for artist in top_artists_medium_term['items']]
    track_data_long_term = [{'name': track['name'], 'artist': track['artists'][0]['name'], 'album': track['album']['name'], 'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None} for track in top_tracks_long_term['items']]
    artist_data_long_term = [{'name': artist['name'], 'image_url': artist['images'][0]['url'] if artist['images'] else None} for artist in top_artists_long_term['items']]
    playlists_data = [{'name': playlist['name'],'description': playlist['description'],'image_url': playlist['images'][0]['url'] if playlist['images'] else None,'playlist_url': playlist['external_urls']['spotify']} for playlist in featured_playlists['playlists']['items']]


    # Fetch and display genres (example logic for recommendations and genres)
    user_top_artists = sp.current_user_top_artists(limit=50, time_range='medium_term')
    top_genres = {}
    for artist in user_top_artists['items']:
        for genre in artist['genres']:
            if genre in top_genres:
                top_genres[genre] += 1
            else:
                top_genres[genre] = 1

    sorted_genres = sorted(top_genres.items(), key=lambda x: x[1], reverse=True)[:30]  # Top 10 genres

    # Pass data to the template
    return render_template(
        'top_tracks.html',
        tracks_short_term=track_data_short_term,
        artists_short_term=artist_data_short_term,
        tracks_medium_term=track_data_medium_term,
        artists_medium_term=artist_data_medium_term,
        tracks_long_term=track_data_long_term,
        artists_long_term=artist_data_long_term,
        top_genres=sorted_genres,
        featured_playlists=playlists_data
    )




if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
