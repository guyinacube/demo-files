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

playlist_id_list = playlist_id_list.select('playlist_id')

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

def get_video_comments_details(youtube, video_id):

    all_comments_details = []

    request = youtube.commentThreads().list(
            part = 'snippet,replies',
            #videoId = ",".join(video_ids),
            videoId = video_id,
            textFormat = 'html',
            maxResults = 5,
            order='time'
        )
    
    response = request.execute()

    for item in response['items']:
        commentdetails = dict(
            CommentID = item.get('etag'),
            ChannelID = item['snippet']['topLevelComment']['snippet'].get('channelId'),
            VideoID = item['snippet']['topLevelComment']['snippet'].get('videoId'),
            Author = item['snippet']['topLevelComment']['snippet'].get('authorDisplayName'),
            AuthorDisplayImageURL = item['snippet']['topLevelComment']['snippet'].get('authorProfileImageUrl'),
            LikeCount = item['snippet']['topLevelComment']['snippet'].get('likeCount', 0),
            ReplyCount = item['snippet']['topLevelComment']['snippet'].get('totalReplyCount', 0),
            CommentDate = item['snippet']['topLevelComment']['snippet'].get('publishedAt'),
            commenttext = item['snippet']['topLevelComment']['snippet'].get('textDisplay')
        )
        all_comments_details.append(commentdetails)

    return all_comments_details

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

video_id_list_output = []
comment_output = []


for listid in playlist_id_list:
    video_id_list_output = get_list_video_ids(youtube,listid)
    for video in video_id_list_output:
        try:
            comment_output.append(get_video_comments_details(youtube,video))
        except:
            pass

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

video_id_list_output = []
comment_output = []


for listid in playlist_id_list:
    video_id_list_output = get_list_video_ids(youtube,listid)
    for video in video_id_list_output:
        try:
            comment_output = get_video_comments_details(youtube,video)
            with open(f'/lakehouse/default/Files/formattedcomments/{video}_comments_{current_datetime}.json', 'w') as json_file:
                json.dump(comment_output, json_file)
        except:
            pass

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
