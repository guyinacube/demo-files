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
from pyspark.sql.window import Window
from pyspark.sql.functions import lead

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName("gold_factdailyvideostats") \
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

windowspec = Window.partitionBy("VideoID").orderBy("CaptureDate")

#bchannelstats = spark.sql("SELECT * FROM YT_LakeHouse.bronze.channelstats order by channel_id, capturedate")
silver_videostats = spark.read.table("silver_videostats")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_videostats = silver_videostats\
    .withColumn("t_likecount", lead("LikeCount", 1).over(windowspec))\
    .withColumn("t_favoritecount", lead("FavoriteCount", 1).over(windowspec))\
    .withColumn("t_commentcount", lead("CommentCount", 1).over(windowspec))\
    .withColumn("t_viewcount", lead("ViewCount", 1).over(windowspec))

silver_videostats = silver_videostats\
    .withColumn("DailyLikeCount", silver_videostats["t_likecount"] - silver_videostats["LikeCount"])\
    .withColumn("DailyFavoriteCount", silver_videostats["t_favoritecount"] - silver_videostats["FavoriteCount"])\
    .withColumn("DailyCommentCount", silver_videostats["t_commentcount"] - silver_videostats["CommentCount"])\
    .withColumn("DailyViewCount", silver_videostats["t_viewcount"] - silver_videostats["ViewCount"])

silver_dailychannelstats = silver_videostats.select("VideoID","ChannelID","CaptureDate", "DailyLikeCount", "DailyFavoriteCount", "DailyCommentCount", "DailyViewCount")

#bchannelstats.write.mode("overwrite").format("delta").saveAsTable("silver.dailychannelstats")

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

gold_dailyvideostats = silver_dailychannelstats.alias("silver") \
    .join(dimcalendar.alias("calendar"), (silver_dailychannelstats.CaptureDate == dimcalendar.Date), "left") \
    .join(dim_channels.alias("channel"), (silver_dailychannelstats.ChannelID == dim_channels.ChannelAK), "left") \
    .join(dim_videos.alias("video"), (silver_dailychannelstats.VideoID == dim_videos.VideoAK), "left") \
    .select(col("calendar.Date"), \
    col("channel.ChannelSK"),
    col("video.VideoSK"),
    col("silver.DailyLikeCount"),
    col("silver.DailyFavoriteCount"),
    col("silver.DailyCommentCount"),
    col("silver.DailyViewCount")
    ).orderBy(col("video.VideoSK"),col("calendar.Date"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldTable = DeltaTable.forName(spark,"gold_factdailyvideostats")

goldTable.alias("gold") \
    .merge(
        gold_dailyvideostats.alias("updates"),
        'gold.VideoSK = updates.VideoSK AND gold.CaptureDateSK = updates.Date'
    ) \
    .whenNotMatchedInsert( values=
    {
        "CaptureDateSK": "updates.Date",
        "ChannelSK": "updates.ChannelSK",
        "VideoSK": "updates.VideoSK",
        "LikeCount": "updates.DailyLikeCount",
        "ViewCount": "updates.DailyViewCount",
        "FavoriteCount": "updates.DailyFavoriteCount",
        "CommentCount": "updates.DailyCommentCount"
    }) \
    .whenMatchedUpdate( set =
    {
            "LikeCount": "updates.DailyLikeCount",
        "ViewCount": "updates.DailyViewCount",
        "FavoriteCount": "updates.DailyFavoriteCount",
        "CommentCount": "updates.DailyCommentCount"
    }
    )\
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
