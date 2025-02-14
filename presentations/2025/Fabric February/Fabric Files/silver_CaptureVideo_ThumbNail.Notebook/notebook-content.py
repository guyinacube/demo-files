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

import json
import requests
import requests
from datetime import datetime
from pyspark.sql.functions import when, lit, col, current_timestamp, input_file_name, regexp_replace, concat, lit, trim

current_date = datetime.now().strftime('%Y%m%d')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos_all = spark.read.option("multiline", "true").json(f"Files/bronze/videometrics/*_videometrics_{current_date}.json") 

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos = videos_all.dropDuplicates(['VideoID'])
videos = videos.withColumn("ThumbNailURL", trim(concat(lit("https://i.ytimg.com/vi/"), col('VideoID'), lit("/hqdefault.jpg"))))


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videos = videos \
    .select(col('VideoID')  
    ,col("ThumbNailURL")
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

def download_thumbnail (video_id, image_url):

    # Send a GET request
    response = requests.get(image_url, stream=True)

    # Save the image
    with open(f'/lakehouse/default/Files/bronze/videothumbnails/{video_id}.jpg', 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)

    del response

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

videocollect = videos.collect()

for video in videocollect:
    image_url = video['ThumbNailURL']
    video_id = video['VideoID']
    download_thumbnail(video_id, image_url)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

#Add facial regonition to the process.

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
