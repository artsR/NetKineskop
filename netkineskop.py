import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from jinja2 import contextfilter

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from flask import Flask, request, render_template, redirect, url_for, session, jsonify, Response



BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

CLIENT_SECRET_FILE = 'client_secret.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


@contextfilter()
def format_date(value, input_format, output_format='%Y-%m-%d %H:%M'):
    value_as_datetime = datetime.strptime(value, input_format)
    return value_as_datetime.strftime(output_format)



@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/subscriptions')
def subscriptions():
    if 'credentials' not in session:
        return redirect(url_for('oauth_authorize'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    youtube = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=credentials
    )
    response = youtube.subscriptions().list(part='snippet', mine='true')
    session['credentials'] = credentials_to_dict(credentials)
    subscribed_videos = response.execute()
    imgs = [
        v for k, v in subscribed_videos.items()
    ]
    channel_ids = [
        img['snippet']['resourceId']['channelId']
        for img in imgs[4]
    ]
    # print(','.join(id for id in channel_ids))
    response_videos = youtube.channels().list(
        part='contentDetails',
        id=','.join(id for id in channel_ids)
    )
    videos = response_videos.execute()
    # print(f'##############\n {videos}')
    channels = [{
        'id': video['id'],
        'uploads': video['contentDetails']['relatedPlaylists']['uploads']
        }
        for video in videos['items']
    ]
    from pprint import pprint
    print(f'Channels ######## : {channels}')
    uploads = list()
    for channel in channels:
        response_vids = youtube.playlistItems().list(
            part='snippet, contentDetails',
            playlistId=channel['uploads'],
            maxResults=50,
            pageToken=None
        )
        uploads.append(response_vids.execute())

    videos_all = list()
    for vids in uploads:
        for vid in vids['items']:
            videos_all.append({
                'channel_id': vid['snippet']['channelId'],
                'channel_title': vid['snippet']['channelTitle'],
                'published_at': vid['snippet']['publishedAt'],
                'thumbnail_url': vid['snippet']['thumbnails']['medium']['url'],
                'video_title': vid['snippet']['title'],
                'video_url': vid['snippet']['resourceId']['videoId']
        })
    pprint(videos_all)
    return render_template('imgs.html', imgs=imgs, videos=videos_all)


@app.route('/authorize')
def oauth_authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES
    )
    flow.redirect_uri = url_for('oauth_callback', _external=True)
    authorization_url, state = flow.authorization_url(
        access_type='offline', include_granted_scopes='true'
    )
    session['state'] = state

    return redirect(authorization_url)


@app.route('/callback')
def oauth_callback():
    state = session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = url_for('oauth_callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('subscriptions'))


@app.route('/revoke')
def oauth_revoke():
    if 'credentials' not in session:
        return (
            f'You need to <a href="/authorize">authorize</a> '
            f'before testing the code to revoke credentials.'
        )

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    revoke = requests.post(
        'https://oauth2.googleapis.com/revoke',
        params={'token': credentials.token},
        headers={'content-type': 'application/x-www-form-urlencoded'}
    )

    status_code = getattr(revoke, 'status_code')
    if status_code == 200:
        return 'Credentials successfully revoked.'
    else:
        return 'An error occured.'


@app.route('/clear')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    return 'Credentials have been cleared.<br><br>'


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }



if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
