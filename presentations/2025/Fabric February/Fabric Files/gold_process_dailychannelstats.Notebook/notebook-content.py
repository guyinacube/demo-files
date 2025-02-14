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
    .tableName("gold_factdailychannelstats") \
    .addColumn("CaptureDateSK", DateType()) \
    .addColumn("ChannelSK", IntegerType()) \
    .addColumn("SubscriberCount", IntegerType()) \
    .addColumn("ViewCount", IntegerType()) \
    .addColumn("VideoCount", IntegerType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

windowspec = Window.partitionBy("ChannelID").orderBy("CaptureDate")

#bchannelstats = spark.sql("SELECT * FROM YT_LakeHouse.bronze.channelstats order by channel_id, capturedate")
silver_channelstats = spark.read.table("silver_channelstats")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_channelstats = silver_channelstats\
    .withColumn("t_subcount", lead("SubscriberCount", 1).over(windowspec))\
    .withColumn("t_videocount", lead("VideoCount", 1).over(windowspec))\
    .withColumn("t_viewcount", lead("ViewCount", 1).over(windowspec))

silver_channelstats = silver_channelstats\
    .withColumn("DailySubscriberCount", silver_channelstats["t_subcount"] - silver_channelstats["SubscriberCount"])\
    .withColumn("DailyVideoCount", silver_channelstats["t_videocount"] - silver_channelstats["VideoCount"])\
    .withColumn("DailyViewCount", silver_channelstats["t_viewcount"] - silver_channelstats["ViewCount"])

silver_dailychannelstats = silver_channelstats.select("ChannelID","ChannelID","CaptureDate", "ChannelName", "DailySubscriberCount", "DailyVideoCount", "DailyViewCount")

#bchannelstats.write.mode("overwrite").format("delta").saveAsTable("silver.dailychannelstats")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

dimcalendar = spark.read.table("gold_calendar")
dim_channels = spark.read.table("gold_dimchannels")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

gold_dailychannelstats = silver_dailychannelstats.alias("silver") \
    .join(dimcalendar.alias("calendar"), (silver_dailychannelstats.CaptureDate == dimcalendar.Date), "left") \
    .join(dim_channels.alias("channel"), (silver_dailychannelstats.ChannelID == dim_channels.ChannelAK), "left") \
    .select(col("calendar.Date"), \
    col("channel.ChannelSK"),
    col("silver.DailySubscriberCount"),
    col("silver.DailyViewCount"),
    col("silver.DailyVideoCount")
    ).orderBy(col("channel.ChannelSK"),col("calendar.Date"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldTable = DeltaTable.forName(spark,"gold_factdailychannelstats")

goldTable.alias("gold") \
    .merge(
        gold_dailychannelstats.alias("updates"),
        'gold.ChannelSK = updates.ChannelSK AND gold.CaptureDateSK = updates.Date'
    ) \
    .whenNotMatchedInsert( values=
    {
        "CaptureDateSK": "updates.Date",
        "ChannelSK": "updates.ChannelSK",
        "SubscriberCount": "updates.DailySubscriberCount",
        "ViewCount": "updates.DailyViewCount",
        "VideoCount": "updates.DailyVideoCount"
    }
)  .whenMatchedUpdate( set=
    {
        "SubscriberCount": "updates.DailySubscriberCount",
        "ViewCount": "updates.DailyViewCount",
        "VideoCount": "updates.DailyVideoCount"
    }
)\
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
