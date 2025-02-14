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

#from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, FloatType
from pyspark.sql.types import *
from delta.tables import *

from pyspark.sql.functions import when, lit, col, current_timestamp, input_file_name
from datetime import datetime

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

current_date = datetime.now().strftime('%Y%m%d')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

channel_stats = spark.read.option("multiline", "true").json(f"Files/bronze/channelmetrics/channelmetrics_{current_date}.json")

channel_stats = channel_stats.withColumn("FileName", input_file_name()) \
    .withColumn("ModifiedDate", current_timestamp())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('silver_channelstats') \
    .addColumn('CaptureDate', DateType()) \
    .addColumn('ChannelID', StringType()) \
    .addColumn('ChannelName', StringType()) \
    .addColumn('PlayListID', StringType()) \
    .addColumn('SubscriberCount', IntegerType()) \
    .addColumn('VideoCount', IntegerType()) \
    .addColumn('ViewCount', IntegerType()) \
    .addColumn('FileName', StringType()) \
    .addColumn('ModifiedDate', DateType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# https://sparkbyexamples.com/pyspark/pyspark-window-functions/

# CELL ********************



deltaTable_source = DeltaTable.forName(spark, 'silver_channelstats')

channel_statsUpdate = channel_stats

deltaTable_source.alias('silver')\
    .merge(
        channel_statsUpdate.alias('update'),
        'silver.ChannelID = update.channel_id and silver.CaptureDate = update.capturedate'
    ) \
    .whenNotMatchedInsert( values =
        {
            "CaptureDate": "update.capturedate",
            "ChannelID": "update.channel_id",
            "ChannelName": "update.channel_name",
            "PlayListID": "update.playlist_id",
            "SubscriberCount": "update.subscribercount",
            "VideoCount": "update.videocount",
            "ViewCount": "update.viewcount",
            "FileName": "update.FileName",
            "ModifiedDate": "update.ModifiedDate"
        }
    )\
    .whenMatchedUpdate( set =
        {
            "ChannelName": "update.channel_name",
            "PlayListID": "update.playlist_id",
            "SubscriberCount": "update.subscribercount",
            "VideoCount": "update.videocount",
            "ViewCount": "update.viewcount",
            "FileName": "update.FileName",
            "ModifiedDate": "update.ModifiedDate"
        }
    ) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
