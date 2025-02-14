# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "a860b13e-0523-4df8-a3cb-b44b81e9a4d7",
# META       "default_lakehouse_name": "Comments_Analysis",
# META       "default_lakehouse_workspace_id": "97dc8aaf-6f99-4fee-ae59-a4f47ec3c596"
# META     }
# META   }
# META }

# CELL ********************

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType

import base64
import requests

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### Define function: Text sentiment for video comments

# CELL ********************

# About NLTK: https://www.geeksforgeeks.org/nltk-sentiment-analysis-tutorial-for-beginners/

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize NLTK's SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

# Define UDF for sentiment analysis
def analyze_sentiment(text):
    sentiment = sia.polarity_scores(text)
    return sentiment['compound']

sentiment_udf = udf(analyze_sentiment, StringType())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

delta_table_path = "Tables/CommentsWithSentiment"

df = spark.read.option("multiline", "true").json("Files/formattedcomments/*_comments_20250204.json")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************


# df now is a Spark DataFrame containing JSON data from "Files/formattedcomments/3smvZqaRjBU_comments_20250204.json".
df = df.withColumn("textSentiment", sentiment_udf(df["commenttext"]).cast("double"))

# Overwrite the Delta table with the updated DataFrame
df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(delta_table_path)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC select*
# MAGIC From CommentsWithSentiment cws
# MAGIC limit 1000


# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
