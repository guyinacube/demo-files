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
from pyspark.sql.functions import *

current_datetime = datetime.now()
current_date = datetime.now().strftime('%Y%m%d')
current_date_dashed = datetime.now().strftime('%Y-%m-%d')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_date_dashed

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

# MARKDOWN ********************

# ## Function to get channel statistics

# CELL ********************

def get_channel_statistics (youtube, channelids):

    all_channel_data = []

    channel_request = youtube.channels().list(
        part = 'snippet,contentDetails,statistics',
        id = ','.join(channelids)
    )

    channel_response = channel_request.execute()

    for i in range(len(channel_response['items'])):
        channel_data = dict(
            channel_id = channel_response['items'][i]['id'],
            channel_name = channel_response['items'][i]['snippet']['title'],
            subscribercount = channel_response['items'][i]['statistics']['subscriberCount'],
            viewcount = channel_response['items'][i]['statistics']['viewCount'],
            videocount = channel_response['items'][i]['statistics']['videoCount'],
            playlist_id = channel_response['items'][i]['contentDetails']['relatedPlaylists']['uploads'],
            capturedate = current_date_dashed
            )
        all_channel_data.append(channel_data)

    return all_channel_data

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

channel_stats_output = get_channel_statistics(youtube, channelids)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

print(channel_stats_output)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

with open(f'/lakehouse/default/Files/bronze/channelmetrics/channelmetrics_{current_date}.json', 'w') as json_file:
    json.dump(channel_stats_output, json_file)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
