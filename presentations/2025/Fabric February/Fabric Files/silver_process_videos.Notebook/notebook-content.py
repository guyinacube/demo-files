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
#current_date = '20250101'

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos_all = spark.read.option("multiline", "true").json(f"Files/bronze/videometrics/*_videometrics_{current_date}.json") 
#videos_all = spark.read.option("multiline", "true").json(f"Files/bronze/videometrics/*_videometrics_*.json") 

videos_all = videos_all.withColumn("ModifiedDate", current_timestamp()) \
    .withColumn("FileName", input_file_name()) \
    .withColumn("CaptureDate", lit(datetime.now().strftime("%Y-%m-%d")))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos = videos_all.dropDuplicates(['VideoID']) \
    .select(col('VideoID')
    ,col('Title') 
    ,col('VideoDescr') 
    ,col('PublishedDate') 
    ,col('ModifiedDate') 
    ,col('FileName')
    ,col('ChannelID'))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos = videos \
    .withColumn("Hosts", \
    when((videos.VideoDescr.contains("Adam")) & (videos.ChannelID == "UCFp1vaKzpfvoGai0vE5VJ0w"), "Adam Saxton")\
    .when((videos.VideoDescr.contains("Patrick")) & (videos.ChannelID == "UCFp1vaKzpfvoGai0vE5VJ0w"), "Patrick LeBlanc")
    .when((videos.VideoDescr.contains("Join us live")) & (videos.ChannelID == "UCFp1vaKzpfvoGai0vE5VJ0w"), "Guy In a Cube")
    .when(videos.ChannelID == "UCVKOYTWTU3LLqG-S-aiEVGg", "Patrick LeBlanc")
    .when(videos.ChannelID == "UCy--PYvwBwAeuYaR8JLmrfg", "Power BI")
    .when(videos.ChannelID == "UCH0gDiJ1RSn3kkxRQnQaH1w", "Fabric")
    .when((~videos.VideoDescr.contains("Patrick")) & (videos.ChannelID == "UCFp1vaKzpfvoGai0vE5VJ0w") 
        & (videos.VideoDescr.contains("patrickdba")), "Guest") 
    .otherwise("Guest")
    ) \
    .withColumn("LiveStream", \
    when(videos.VideoDescr.contains("Join us live"), "Yes")
    .otherwise("No") )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('silver_videos') \
    .addColumn('VideoID', StringType()) \
    .addColumn('PublishedDate', DateType()) \
    .addColumn('VideoDescr', StringType()) \
    .addColumn('Title', StringType()) \
    .addColumn('FileName', StringType()) \
    .addColumn('LiveStream', StringType()) \
    .addColumn('ChannelID', StringType()) \
    .addColumn('ModifiedDate', DateType()) \
    .addColumn("Hosts", StringType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

silver_videos = DeltaTable.forName(spark, 'silver_videos')


silver_videos.alias('silver')\
    .merge(
        videos.alias('update'),
        'silver.VideoID = update.VideoID'
    ) \
    .whenNotMatchedInsert( values =
        {
            "VideoID": "update.VideoID",
            "PublishedDate": "update.PublishedDate",
            "VideoDescr": "update.VideoDescr",
            "Title": "update.Title",
            "FileName": "update.FileName",
            "LiveStream": "update.LiveStream",
            "ChannelID": "update.ChannelID",
            "ModifiedDate": "update.ModifiedDate",
            "Hosts": "update.Hosts"
        }
    ) \
    .whenMatchedUpdate(set =
    {
            "Hosts": "update.Hosts",
            "ModifiedDate": "update.ModifiedDate"
    }) \
    .execute()


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# https://sparkbyexamples.com/pyspark/pyspark-window-functions/
