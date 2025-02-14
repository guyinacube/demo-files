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
# META       "default_lakehouse_workspace_id": "97dc8aaf-6f99-4fee-ae59-a4f47ec3c596"
# META     }
# META   }
# META }

# CELL ********************

from pyspark.sql.types import *
from delta.tables import *
from pyspark.sql.functions import col
from delta.tables import *
from pyspark.sql.functions import monotonically_increasing_id, col, when, coalesce, max, lit

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('gold_DimVideos') \
    .addColumn('VideoSK', IntegerType()) \
    .addColumn('ChannelSK', IntegerType()) \
    .addColumn('VideoAK', StringType()) \
    .addColumn('Title', StringType()) \
    .addColumn('Descr', StringType()) \
    .addColumn('LiveStream', StringType()) \
    .addColumn('PublishedDate', DateType()) \
    .addColumn('Hosts', StringType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_videos = spark.read.table("silver_videos")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_videos = silver_videos \
    .dropDuplicates(["VideoID", "Title"]) \
    .select(col("VideoID"), col("Title"), col("ChannelID"), col("VideoDescr") \
        , col("LiveStream"), col("PublishedDate"), col("Hosts"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

gold_DimVideos_hold = spark.read.table("gold_DimVideos")

max_VideoSK = gold_DimVideos_hold.select(coalesce(max(col("VideoSK")), lit(0)).alias("MaxVideoSK")).first()[0]

gold_dimVideo = silver_videos.join(gold_DimVideos_hold,(silver_videos.VideoID == gold_DimVideos_hold.VideoAK), \
    "left_anti")

gold_dimVideo = gold_dimVideo.withColumn("VideoSK", monotonically_increasing_id() + max_VideoSK + 1)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

dim_channels = spark.read.table("gold_dimchannels")

gold_dimVideo = gold_dimVideo.alias("gold") \
    .join(dim_channels.alias("channel"), (gold_dimVideo.ChannelID == dim_channels.ChannelAK), "left") \
    .select(col("gold.VideoSK"), \
    col("channel.ChannelSK"), \
    col("gold.VideoID"), \
    col("gold.Title"), \
    col("gold.VideoDescr"), \
    col("gold.LiveStream"), \
    col("gold.PublishedDate"), \
    col("gold.Hosts") \
    ).orderBy(col("gold.VideoSK"),col("channel.ChannelSK"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldDeltaTable = DeltaTable.forName(spark, "gold_dimvideos")

updates = gold_dimVideo

goldDeltaTable.alias("gold") \
.merge(
    updates.alias("update"),
    "gold.VideoSK = update.VideoID"
) \
.whenNotMatchedInsert( values =
    {
        "VideoSK": "update.VideoSK",
        "VideoAK": "update.VideoID",
        "PublishedDate": "update.PublishedDate",
        "Descr": "update.VideoDescr",
        "Title":"update.Title",
        "LiveStream":"update.LiveStream",
        "ChannelSK":"update.ChannelSK",
        "Hosts": "update.Hosts"
    }
) \
.whenMatchedUpdate( set =
    { 
        "ChannelSK":"update.ChannelSK",
        "Hosts": "update.Hosts"
    }
) \
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
