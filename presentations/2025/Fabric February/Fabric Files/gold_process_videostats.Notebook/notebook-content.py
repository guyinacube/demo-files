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

# MARKDOWN ********************

# look at resources folder in Fabric

# CELL ********************

from pyspark.sql.types import *
from delta.tables import *
from pyspark.sql.functions import col

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName("gold_factvideostats") \
    .addColumn("VideoSK", IntegerType()) \
    .addColumn("CaptureDateSK", DateType()) \
    .addColumn("ChannelSK", IntegerType()) \
    .addColumn("LikeCount", IntegerType()) \
    .addColumn("FavoriteCount", IntegerType()) \
    .addColumn("CommentCount", IntegerType()) \
    .addColumn("ViewCount", IntegerType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

dimcalendar = spark.read.table("gold_calendar")
dim_channels = spark.read.table("gold_dimchannels")
dim_videos = spark.read.table("gold_dimvideos")
silver_videostats = spark.read.table("silver_videostats")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

gold_videostats = silver_videostats.alias("silver") \
    .join(dimcalendar.alias("calendar"), (silver_videostats.CaptureDate == dimcalendar.Date), "left") \
    .join(dim_channels.alias("channel"), (silver_videostats.ChannelID == dim_channels.ChannelAK), "left") \
    .join(dim_videos.alias("video"), (silver_videostats.VideoID == dim_videos.VideoAK), "left") \
    .select(col("calendar.Date"), \
    col("channel.ChannelSK"),
    col("video.VideoSK"),
    col("silver.LikeCount"),
    col("silver.FavoriteCount"),
    col("silver.CommentCount"),
    col("silver.ViewCount")
    ).orderBy(col("video.VideoSK"),col("calendar.Date"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldTable = DeltaTable.forName(spark,"gold_factvideostats")

goldTable.alias("gold") \
    .merge(
        gold_videostats.alias("updates"),
        'gold.VideoSK = updates.VideoSK AND gold.CaptureDateSK = updates.Date'
    ) \
    .whenNotMatchedInsert( values=
    {
        "CaptureDateSK": "updates.Date",
        "ChannelSK": "updates.ChannelSK",
        "VideoSK": "updates.VideoSK",
        "LikeCount": "updates.LikeCount",
        "ViewCount": "updates.ViewCount",
        "FavoriteCount": "updates.FavoriteCount",
        "CommentCount": "updates.CommentCount"
    }
)  \
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
