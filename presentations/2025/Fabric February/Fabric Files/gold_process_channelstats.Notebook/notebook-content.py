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
    .tableName("gold_factchannelstats") \
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

dimcalendar = spark.read.table("gold_calendar")
dim_channels = spark.read.table("gold_dimchannels")
silver_channelstats = spark.read.table("silver_channelstats")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

gold_channelstats = silver_channelstats.alias("silver") \
    .join(dimcalendar.alias("calendar"), (silver_channelstats.CaptureDate == dimcalendar.Date), "left") \
    .join(dim_channels.alias("channel"), (silver_channelstats.ChannelID == dim_channels.ChannelAK), "left") \
    .select(col("calendar.Date"), \
    col("channel.ChannelSK"),
    col("silver.SubscriberCount"),
    col("silver.ViewCount"),
    col("silver.VideoCount")
    ).orderBy(col("channel.ChannelSK"),col("calendar.Date"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

gold_channelstats.show(200)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldTable = DeltaTable.forName(spark,"gold_factchannelstats")

goldTable.alias("gold") \
    .merge(
        gold_channelstats.alias("updates"),
        'gold.ChannelSK = updates.ChannelSK AND gold.CaptureDateSK = updates.Date'
    ) \
    .whenNotMatchedInsert( values=
    {
        "CaptureDateSK": "updates.Date",
        "ChannelSK": "updates.ChannelSK",
        "SubscriberCount": "updates.SubscriberCount",
        "ViewCount": "updates.ViewCount",
        "VideoCount": "updates.VideoCount"
    }
)  \
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC select *
# MAGIC from gold_factchannelstats where ChannelSK = 4

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
