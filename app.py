from flask import Flask, redirect, request, url_for, session, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

# Spotify API credentials (replace with your actual credentials)
SPOTIPY_CLIENT_ID = 'ad274f1907e7485e826c2979ca114830'
SPOTIPY_CLIENT_SECRET = 'da13ee6f543645e8867ea7d28399c1cf'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:5000/callback'

# Spotify OAuth setup
sp_oauth = SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                        client_secret=SPOTIPY_CLIENT_SECRET,
                        redirect_uri=SPOTIPY_REDIRECT_URI,
                        scope='user-top-read playlist-modify-public')

@app.route('/')
def home():
    # Generate Spotify authorization URL
    auth_url = sp_oauth.get_authorize_url()
    return render_template('index.html', auth_url=auth_url)

@app.route('/callback')
def callback():
    # Handle the redirect from Spotify login
    session.clear()  # Clear session data before starting new login flow
    code = request.args.get('code')  # Get the authorization code from the callback URL
    
    if code:
        # Exchange the authorization code for an access token
        token_info = sp_oauth.get_access_token(code)
        session['token_info'] = token_info  # Store token in session

        return redirect('/top-tracks')  # Redirect user to a new page (e.g., top tracks)
    
    return redirect('/')  # Redirect to homepage if something goes wrong



@app.route('/top-tracks')
def top_tracks():
    token_info = session.get('token_info', None)

    if not token_info:
        return redirect('/')  # If no token, redirect to homepage
    
    # Create a Spotipy client with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Fetch user's top tracks
    top_tracks = sp.current_user_top_tracks(limit=10)
    
    # Extract track names from the data
    track_names = [track['name'] for track in top_tracks['items']]

    # Pass track names to the HTML template to display
    return render_template('top_tracks.html', tracks=track_names)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use PORT from environment variable or default to 5000
    app.run(host='0.0.0.0', port=port)
