import os
import requests
from dotenv import load_dotenv


BASEDIR = os.path.join(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, 'env'))


yt_api_key = os.environ.get('YT_API_KEY')

channel = 'UC5n4fhgP2F-u9c_bEIO4jzw'

# response = requests.get(
# f'https://www.googleapis.com/youtube/v3/subscriptions?part=snippet%2CcontentDetails&channelId=UC4rasfm9J-X4jNl9SvXp8xA&key={yt_api_key}'
# )
# print(response)

### Resources and resource types
# subscription
# video
# videoCategory
# guideCategory

### Partial resources
# part
# fields

import google_auth_oauthlib.flow
import googleapiclient.discovery.build
import googleapiclient.errors

scopes = ['https://www.googleapis.com/auth/youtube.readonly']

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    api_service_name = 'youtube'
    api_version = 'v3'
    client_secrets_file = 'client_secret.json'

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.subscriptions().list(
        part='snippet',
        mine='true'
    )
    response = request.execute()
    from pprint import pprint as pp
    pp(response)

if __name__ == "__main__":
    main()
