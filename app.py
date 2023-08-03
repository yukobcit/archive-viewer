import os
import requests
from flask import Flask, g
from flask_cors import CORS
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)

# Get tokens
client_id = os.environ.get('TWITCH_CLIENT_ID')
client_secret = os.environ.get('TWITCH_CLIENT_SECRET')


# Get Twitch token
def get_twitch_access_token(client_id, client_secret):
    token_url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }

    response = requests.post(token_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['access_token']
    else:
        print(f"Failed to get access token. Status code: {response.status_code}")
        return None


def get_user_id(username):
    url = f'https://api.twitch.tv/helix/users?login={username}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to get video info. Status code: {response.status_code}")
        return None


def get_all_followers(username):
    user = get_user_id(username)
    print("user_id", user['data'][0]['id'])
    user_id = user['data'][0]['id']

    url = f'https://api.twitch.tv/helix/users/follows'
    params = {
        'from_id': user_id,
        'first': 100  # numbers of channels to fetch
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return [follow['to_id'] for follow in data['data']]
    else:
        print(f"Failed to get user following. Status code: {response.status_code}")
        return []


def get_channel_videos(channel_id, client_id, video_type):
    url = 'https://api.twitch.tv/helix/videos'

    params = {
        'user_id': channel_id,
        'first': 1,
        'type': video_type,
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        videos = data['data']

        # filter with two weeks period
        two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
        recent_videos = [video for video in videos if
                         datetime.fromisoformat(video['published_at'][:-1]) >= two_weeks_ago]

        return recent_videos
    else:
        print(f"Failed to get videos. Status code: {response.status_code}")
        return None


def get_channel_clips(channel_id, client_id):
    url = 'https://api.twitch.tv/helix/clips'

    two_weeks_ago = datetime.utcnow() - timedelta(weeks=2)
    two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        'broadcaster_id': channel_id,
        'first': 1,
        'started_at': two_weeks_ago_str,
        'ended_at': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-Id': client_id
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print(f"Failed to get videos. Status code: {response.status_code}")
        return None


def get_items_by_each_follower(video_type=None, username=None, parameter=None):
    print(video_type, username, parameter)
    following_channels = get_all_followers(username)

    # Loop each follower user_id
    if following_channels:
        all_videos = []
        for channel_id in following_channels:
            if parameter == "videos":
                videos = get_channel_videos(channel_id, client_id, video_type)
            elif parameter == "clips":
                videos = get_channel_clips(channel_id, client_id)
            all_videos.extend(videos)

        all_videos_sorted = sorted(all_videos, key=lambda x: x['created_at'], reverse=True)

        return all_videos_sorted
    else:
        print("Failed to get following channels.")

    return


@app.route('/videos/<video_type>/<username>')
def get_videos_by_follower(video_type, username):
    result = get_items_by_each_follower(video_type, username, "videos")
    return result


@app.route('/clips/<username>')
def get_clips_by_follower(username):
    result = get_items_by_each_follower(username=username, parameter="clips")
    return result


access_token = get_twitch_access_token(client_id, client_secret)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
