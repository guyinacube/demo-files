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

from pyspark.sql.functions import *
from pyspark.sql.types import *
from datetime import *
from delta.tables import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

initial_date_load = False

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

if initial_date_load:
    start_date = '2024-12-25'
    end_date = datetime.now().strftime('%Y-%m-%d')
else:
    #start_date = '2025-02-09'
    #end_date = '2025-02-10'
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    



# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

spark.sql(f" \
    select \
        explode( \
                sequence( \
                        to_date('{start_date}'), \
                        to_date('{end_date}'), \
            interval 1 day)) \
    as calendardate") \
.createOrReplaceTempView('calendar')

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

_cal = spark.sql("select \
    calendardate as Cal_Date, \
    year(calendardate) Cal_Year, \
    date_format(calendardate, 'MMMM') Cal_Month, \
    date_format(calendardate, 'MMM') Cal_Month_Abbrev, \
    month(calendardate) Cal_Month_Number, \
    dayofweek(calendardate) Cal_Day_Of_Week, \
    date_format(calendardate, 'EEEE') Cal_Day, \
    date_format(calendardate, 'EEE') Cal_Day_Abbrev \
from calendar")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

_cal.show()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

DeltaTable.createIfNotExists(spark) \
    .tableName('gold_calendar') \
    .addColumn('Date', DateType()) \
    .addColumn('Year', IntegerType()) \
    .addColumn('MonthName', StringType()) \
    .addColumn('MonthNameAbbrev', StringType()) \
    .addColumn('MonthNumber', IntegerType()) \
    .addColumn('DayOfWeek', IntegerType()) \
    .addColumn('DayName', StringType()) \
    .addColumn('DayNameAbbrev', StringType()) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

deltaTable_source = DeltaTable.forName(spark, 'gold_calendar')

calendar_update = _cal

deltaTable_source.alias('gold')\
    .merge(
        calendar_update.alias('update'),
        'gold.Date = update.Cal_Date'
    ) \
    .whenNotMatchedInsert( values =
        {
            "Date": "update.Cal_Date",
            "Year": "update.Cal_Year",
            "MonthName": "update.Cal_Month",
            "MonthNameAbbrev": "update.Cal_Month_Abbrev",
            "MonthNumber": "update.Cal_Month_Number",
            "DayOfWeek": "update.Cal_Day_Of_Week",
            "DayName": "update.Cal_Day",
            "DayNameAbbrev": "update.Cal_Day_Abbrev"
        }
    )\
    .whenMatchedUpdate( set =
        {
            
        }
    ) \
    .execute()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC 
# MAGIC select *
# MAGIC from gold_calendar

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
