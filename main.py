import requests
import os
from dotenv import load_dotenv

load_dotenv()

client_id = os.environ.get('TWITCH_CLIENT_ID')
client_secret = os.environ.get('TWITCH_CLIENT_SECRET')
user_id = 428757365
video_id = 1882834413
video_type = "archive"

def get_twitch_video_info(video_id, client_id, access_token):
    if access_token:
        url = f'https://api.twitch.tv/helix/videos?id={video_id}'
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
    else:
        print("Failed to get the access token.")
        return None


def get_all_videos(user_id, client_id, access_token, video_type):
    url = 'https://api.twitch.tv/helix/videos'
    params = {
        'user_id': user_id,
        'first': 1,
        'type': video_type
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


def get_channel_videos(channel_id, client_id, access_token):
    url = 'https://api.twitch.tv/helix/videos'
    params = {
        'user_id': channel_id,
        'first': 3  # maximum 100
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
        print(f"Failed to get channel videos. Status code: {response.status_code}")
        return []


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


def get_user_following(user_id, client_id, access_token):
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


if __name__ == "__main__":
    access_token = get_twitch_access_token(client_id, client_secret)
    if access_token:

        result = get_twitch_video_info(video_id, client_id, access_token)
        print(result)

        all_videos = get_all_videos(user_id, client_id, access_token, video_type)
        print(all_videos)

        following_channels = get_user_following(user_id, client_id, access_token)
        if following_channels:
            all_videos = []
            for channel_id in following_channels:
                videos = get_channel_videos(channel_id, client_id, access_token)
                all_videos.extend(videos)

            all_videos_sorted = sorted(all_videos, key=lambda x: x['created_at'])

            for video in all_videos_sorted:
                print(video)
        else:
            print("Failed to get following channels.")
    else:
        print("Failed to get the access token.")
