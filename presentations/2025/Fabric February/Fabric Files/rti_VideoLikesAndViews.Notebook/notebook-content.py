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
%pip install azure_eventhub

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
from azure.eventhub import EventHubProducerClient,EventData
import os
from pyspark.sql.functions import when, lit, col, current_timestamp, input_file_name, to_date

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

video_id = '5I8yzn8oDAo'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_datetime = datetime.now().strftime('%Y-%m-%d')
capturetime = datetime.now().strftime('%H:%M:%s')


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

api_key = mssparkutils.credentials.getSecret('https://pbipvkeyvalut.vault.azure.net/', 'pdlytubeapikey')
channelid = 'UCFp1vaKzpfvoGai0vE5VJ0w' #giac

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

def get_channel_playlistids (youtube, channelid):

    all_playlist_ids = []

    channel_request = youtube.channels().list(
        part = 'snippet,contentDetails,statistics',
        id = channelid
        #id = ','.join(channelids)
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

playlist_ids_output = get_channel_playlistids(youtube, channelid)

playlist_id_list = spark.createDataFrame(playlist_ids_output)

playlist_id_list = playlist_id_list.select('playlist_id')

playlist_id_list = playlist_id_list.rdd.map(lambda x: x.playlist_id).collect()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def get_video_details(youtube, video_id):

    all_video_stats = []


    request = youtube.videos().list(
            part = 'snippet, statistics',
            id = video_id
            #id = ",".join(video_ids[i:i+50])
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

def send_rti_video_event (video_id, morelikes, moreviews, morecomments):
    
    eventhubname = 'es_82c3b774-01cb-4db1-b45f-76796f1e7106'
    eventhubendpoint = '<ENDPOINT>'

    producer = EventHubProducerClient.from_connection_string(conn_str=eventhubendpoint, eventhub_name=eventhubname)
    event_data_batch = producer.create_batch()

    reading = {
        'video_id': video_id,
        'morelikes': morelikes,
        'moreviews': moreviews,
        'morecomments': morecomments,
        'currentdate' : current_datetime,
        'currenttime' : capturetime
    }

    send_reading = json.dumps(reading)

    event_data_batch.add(EventData(send_reading))

    producer.send_batch(event_data_batch)

    producer.close()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

video_stats_output = video_stats_output = get_video_details(youtube, video_id)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

with open(f'/lakehouse/default/Files/bronze/rti_videostats/{video_id}.json', 'w') as json_file:
    json.dump(video_stats_output, json_file)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_video_stats = spark.read.option("multiline", "true").json(f"Files/bronze/rti_videostats/{video_id}.json") 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_video_stats = current_video_stats.withColumn("CaptureDateTime", current_timestamp())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_video_stats = current_video_stats.select \
    (col('VideoID')
    ,col('ViewCount')
    ,col('LikeCount')
    ,col('CommentCount')
    ,col("CaptureDateTime"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_video_stats.createOrReplaceTempView("current_video_stats")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

data_to_send_to_eventstreamn = spark.sql("SELECT \
    CASE WHEN current_stats.ViewCount > previous.ViewCount THEN current_stats.ViewCount - previous.ViewCount ELSE 0 END MoreViews, \
    CASE WHEN current_stats.LikeCount > previous.LikeCount THEN current_stats.LikeCount - previous.LikeCount ELSE 0 END MoreLikes, \
    CASE WHEN current_stats.CommentCount > previous.CommentCount THEN current_stats.CommentCount - previous.CommentCount ELSE 0 END MoreComments \
FROM rti_previous_video_stats previous \
INNER JOIN current_video_stats current_stats \
ON previous.VideoID = current_stats.VideoID")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_datetime = datetime.now().strftime('%Y-%m-%d')
capturetime = datetime.now().strftime('%H:%M:%s')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

try:
    more_views = data_to_send_to_eventstreamn.select('MoreViews').head()[0]
    more_likes = data_to_send_to_eventstreamn.select('MoreLikes').head()[0]
    more_comments = data_to_send_to_eventstreamn.select('MoreComments').head()[0]
    send_rti_video_event(video_id, more_likes, more_views, more_comments)
except:
    Nothing


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_video_stats.write.format('delta').mode('overwrite').saveAsTable('rti_previous_video_stats')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
