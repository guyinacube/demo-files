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


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('gold_DimChannels') \
    .addColumn('ChannelSK', IntegerType()) \
    .addColumn('ChannelAK', StringType()) \
    .addColumn('PlayListID', StringType()) \
    .addColumn('ChannelName', StringType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#silver_channels = spark.sql("select * from silver_channels")#
silver_channels = spark.read.table("silver_channels")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_channels.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_channels = silver_channels \
    .dropDuplicates(["ChannelID", "ChannelName"]) \
    .select(col("ChannelID"), col("ChannelName"), col("PlayListID"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import monotonically_increasing_id, col, when, coalesce, max, lit
gold_DimChannel_hold = spark.read.table("gold_DimChannels")

max_ChannelSK = gold_DimChannel_hold.select(coalesce(max(col("ChannelSK")), lit(0)).alias("MaxChannelSK")).first()[0]

gold_dimChannel = silver_channels.join(gold_DimChannel_hold,(silver_channels.ChannelID == gold_DimChannel_hold.ChannelAK), "left_anti")

gold_dimChannel = gold_dimChannel.withColumn("ChannelSK", monotonically_increasing_id() + max_ChannelSK + 1)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

goldDeltaTable = DeltaTable.forName(spark, "gold_dimchannels")

updates = gold_dimChannel

goldDeltaTable.alias("gold") \
.merge(
    updates.alias("update"),
    "gold.ChannelSK = update.ChannelID"
) \
.whenNotMatchedInsert( values =
    {
        "ChannelSK": "update.ChannelSK",
        "ChannelAK": "update.ChannelID",
        "PlayListID": "update.PlayListID",
        "ChannelName": "update.ChannelName"
    }
) \
.execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
