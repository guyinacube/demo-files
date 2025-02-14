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

from pyspark.sql.functions import when, lit, col, current_timestamp, input_file_name, to_date
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

#videos_all = spark.read.option("multiline", "true").json(f"Files/bronze/videometrics/*_videometrics_{current_date}.json") 
videos_all = spark.read.option("multiline", "true").json(f"Files/bronze/videometrics/*_videometrics_*.json") 

videos_all = videos_all.withColumn("ModifiedDate", current_timestamp()) \
    .withColumn("FileName", input_file_name()) 

videos_all = videos_all.withColumn("CaptureDateInt", videos_all.FileName.substr(-13,13).substr(1,8))

videos_all = videos_all.withColumn("CaptureDate", to_date(col("CaptureDateInt").cast("string"), "yyyyMMdd"))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videostats = videos_all.select \
    (col('VideoID')
    ,col('ViewCount') 
    ,col('CommentCount') 
    ,col('FavoriteCount') 
    ,col('LikeCount') 
    ,col('ChannelID')
    ,col('CaptureDate')
    ,col('FileName')
    ,col('ModifiedDate'))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('silver_videostats') \
    .addColumn('VideoID', StringType()) \
    .addColumn('ChannelID', StringType()) \
    .addColumn('CaptureDate', DateType()) \
    .addColumn('ModifiedDate', DateType()) \
    .addColumn('LikeCount', IntegerType()) \
    .addColumn('ViewCount', IntegerType()) \
    .addColumn('CommentCount', IntegerType()) \
    .addColumn('FavoriteCount', IntegerType()) \
    .addColumn('FileName', StringType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_videostats = DeltaTable.forName(spark, 'silver_videostats')


silver_videostats.alias('silver')\
    .merge(
        videostats.alias('update'),
        'silver.VideoID = update.VideoID and silver.CaptureDate = update.CaptureDate'
    ) \
    .whenNotMatchedInsert( values =
        {
            "VideoID": "update.VideoID",
            "ChannelID": "update.ChannelID",
            "CaptureDate": "update.CaptureDate",
            "LikeCount": "update.LikeCount",
            "ViewCount": "update.ViewCount",
            "CommentCount": "update.CommentCount",
            "FavoriteCount": "update.FavoriteCount",
            "ModifiedDate": "update.ModifiedDate",
            "FileName": "update.FileName"
        }
    ) \
    .execute()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# https://sparkbyexamples.com/pyspark/pyspark-window-functions/
