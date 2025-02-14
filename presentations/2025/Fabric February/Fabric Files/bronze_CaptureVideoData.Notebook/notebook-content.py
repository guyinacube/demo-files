# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "7753f722-3ed4-4d13-a8d7-a58129461435",
# META       "default_lakehouse_name": "YT_LakeHouse",
# META       "default_lakehouse_workspace_id": "97dc8aaf-6f99-4fee-ae59-a4f47ec3c596",
# META       "known_lakehouses": [
# META         {
# META           "id": "7753f722-3ed4-4d13-a8d7-a58129461435"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

%pip install google-api-python-client

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import requests
from datetime import datetime
import urllib.request

current_datetime = datetime.now().strftime('%Y%m%d')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

api_key = mssparkutils.credentials.getSecret('https://pbipvkeyvalut.vault.azure.net/', 'pdlytubeapikey')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#api_key = 'AIzaSyC48lYmgIQxXChjxOg7zZS2JFnZ26MaMJ0' 
channelid = 'UCFp1vaKzpfvoGai0vE5VJ0w' #giac

channelids = [
    'UCFp1vaKzpfvoGai0vE5VJ0w', #giac
    'UCy--PYvwBwAeuYaR8JLmrfg', #msftpbi
    'UCVKOYTWTU3LLqG-S-aiEVGg', #pleblanc1972
    'UCH0gDiJ1RSn3kkxRQnQaH1w' #msftfabric
]

youtube = build(
    'youtube',
    'v3',
    developerKey = api_key
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def get_channel_playlistids (youtube, channelids):

    all_playlist_ids = []

    channel_request = youtube.channels().list(
        part = 'snippet,contentDetails,statistics',
        id = ','.join(channelids)
    )

    channel_response = channel_request.execute()

    for i in range(len(channel_response['items'])):
        channel_data = dict(
            channel_id = channel_response['items'][i]['id'],
            channel_name = channel_response['items'][i]['snippet']['title'],
            playlist_id = channel_response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
            )
        all_playlist_ids.append(channel_data)

    return all_playlist_ids

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

playlist_ids_output = get_channel_playlistids(youtube, channelids)

playlist_id_list = spark.createDataFrame(playlist_ids_output)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

playlist_id_list = playlist_id_list.select('playlist_id')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

playlist_id_list = playlist_id_list.rdd.map(lambda x: x.playlist_id).collect()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## Function to get a list of the video ids

# CELL ********************

def get_list_video_ids(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part = 'contentDetails',
        playlistId = playlist_id,
        maxResults = 50
    )
    response = request.execute()

    video_ids = []

    for i in range(len(response['items'])):
       video_ids.append(
            response['items'][i]['contentDetails']['videoId']
       )
    
    next_page_token = response.get('nextPageToken')
    more_pages = True

    while more_pages:
            if next_page_token is None:
                more_pages = False
            else:
                request = youtube.playlistItems().list(
                    part = 'contentDetails',
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token
                )
                response = request.execute() 

                for i in range(len(response['items'])):
                    video_ids.append(
                            response['items'][i]['contentDetails']['videoId']
                    )
              
                next_page_token = response.get('nextPageToken')

    return video_ids

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def get_video_details(youtube, video_ids):

    all_video_stats = []

    for i in range (0, len(video_ids), 50):
        request = youtube.videos().list(
            part = 'snippet, statistics',
            id = ",".join(video_ids[i:i+50])
        )
        response = request.execute()

        for video in response['items']:
            video_stats = dict(
                VideoID = video.get('id'),
                ChannelID = video['snippet'].get('channelId'),
                VideoDescr = video['snippet'].get('description'),
                Title = video['snippet'].get('title'),
                PublishedDate = video['snippet'].get('publishedAt'),
                LiveStream = video['snippet'].get('iveBroadcastContent'),
                CategoryID = video['snippet'].get('categoryId'),
                ViewCount = video['statistics'].get('viewCount'),
                LikeCount = video['statistics'].get('likeCount'),
                DislikeCount = video['statistics'].get('dislikeCount'),
                FavoriteCount = video['statistics'].get('favoriteCount'),
                CommentCount = video['statistics'].get('commentCount'),
                ThumbNail = video['snippet']['thumbnails']['high']
            )
            all_video_stats.append(video_stats)

    return all_video_stats

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

video_id_list_output = []
video_stats_output = []

for listid in playlist_id_list:
   video_id_list_output = get_list_video_ids(youtube,listid)
   video_stats_output = get_video_details(youtube, video_id_list_output)
   
   with open(f'/lakehouse/default/Files/bronze/videometrics/{listid}_videometrics_{current_datetime}.json', 'w') as json_file:
    json.dump(video_stats_output, json_file)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
