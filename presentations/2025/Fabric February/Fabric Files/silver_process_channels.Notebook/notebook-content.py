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

channels_all = spark.read.option("multiline", "true").json(f"Files/bronze/channelmetrics/channelmetrics_{current_date}.json") 

channels_all = channels_all.withColumn("ModifiedDate", current_timestamp()) \
    .withColumn("CaptureDate", lit(datetime.now().strftime("%Y-%m-%d")))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

channels_all = channels_all.dropDuplicates(['channel_id']) \
    .select(col('channel_id') \
    ,col('channel_name') \
    ,col('playlist_id') \
    ,col('ModifiedDate')
    ,col('CaptureDate'))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('silver_channels') \
    .addColumn('CaptureDate', DateType()) \
    .addColumn('ChannelID', StringType()) \
    .addColumn('PlayListID', StringType()) \
    .addColumn('ChannelName', StringType()) \
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



deltaTable_source = DeltaTable.forName(spark, 'silver_channels')

channels_Update = channels_all

deltaTable_source.alias('silver')\
    .merge(
        channels_Update.alias('update'),
        'silver.ChannelID = update.channel_id'
    ) \
    .whenNotMatchedInsert( values =
        {
            "CaptureDate": "update.capturedate",
            "ChannelID": "update.channel_id",
            "ChannelName": "update.channel_name",
            "ModifiedDate": "update.ModifiedDate",
            "PlayListID": "update.playlist_id"
        }
    )\
    .whenMatchedUpdate( set =
        {
            "ChannelName": "update.channel_name",
            "PlayListID": "update.playlist_id",
            "CaptureDate": "update.capturedate",
            "ModifiedDate": "update.ModifiedDate"
        }
    ) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
