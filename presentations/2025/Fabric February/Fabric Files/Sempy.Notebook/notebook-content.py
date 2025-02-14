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

# MARKDOWN ********************

# # Install SemPy

# CELL ********************

%pip install semantic-link
%load_ext sempy

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Show datasets in workspace

# CELL ********************

%load_ext sempy


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

import sempy.fabric as fabric
import pyspark.sql.functions as F

df_datasets = fabric.list_datasets()

df_datasets


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Assign values to variables

# CELL ********************

mydataset = "Metrics_Analytics"
myworkspace = "YouTubeMetrics"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Display model relationships

# CELL ********************

from sempy.relationships import plot_relationship_metadata

relationships = fabric.list_relationships(mydataset)
plot_relationship_metadata(relationships)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Run DMV to check Resident columns
# Order by Temperature desc

# CELL ********************

df_dax = fabric.evaluate_dax(
    mydataset,
    """
    SELECT 
        MEASURE_GROUP_NAME,
        ATTRIBUTE_NAME ,
        DATATYPE ,
        DICTIONARY_SIZE ,
        DICTIONARY_ISPAGEABLE ,
        DICTIONARY_ISRESIDENT ,
        DICTIONARY_TEMPERATURE ,
        DICTIONARY_LAST_ACCESSED
    FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
    ORDER BY [DICTIONARY_TEMPERATURE] DESC
    """)
df_dax.head(20)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%dax {mydataset}
# MAGIC SELECT 
# MAGIC     MEASURE_GROUP_NAME,
# MAGIC     ATTRIBUTE_NAME ,
# MAGIC     DATATYPE ,
# MAGIC     DICTIONARY_SIZE ,
# MAGIC     DICTIONARY_ISPAGEABLE ,
# MAGIC     DICTIONARY_ISRESIDENT ,
# MAGIC     DICTIONARY_TEMPERATURE ,
# MAGIC     DICTIONARY_LAST_ACCESSED
# MAGIC FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
# MAGIC ORDER BY [DICTIONARY_TEMPERATURE] DESC

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # REFRAME SEMANTIC MODEL

# CELL ********************

fabric.refresh_dataset(workspace=myworkspace, dataset=mydataset, refresh_type ="Full")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%dax {mydataset}
# MAGIC SELECT 
# MAGIC     MEASURE_GROUP_NAME,
# MAGIC     ATTRIBUTE_NAME ,
# MAGIC     DATATYPE ,
# MAGIC     DICTIONARY_SIZE ,
# MAGIC     DICTIONARY_ISPAGEABLE ,
# MAGIC     DICTIONARY_ISRESIDENT ,
# MAGIC     DICTIONARY_TEMPERATURE ,
# MAGIC     DICTIONARY_LAST_ACCESSED
# MAGIC FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
# MAGIC ORDER BY [DICTIONARY_TEMPERATURE] DESC

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # Run some DAX
# Sum of Sales, grouped by product color

# CELL ********************

# MAGIC %%dax {mydataset}
# MAGIC 
# MAGIC evaluate
# MAGIC SUMMARIZECOLUMNS(
# MAGIC     'gold_calendar'[MonthNameAbbrev] ,
# MAGIC     "View" , SUM('gold_factdailyvideostats'[ViewCount])
# MAGIC )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%dax {mydataset}
# MAGIC SELECT 
# MAGIC     MEASURE_GROUP_NAME,
# MAGIC     ATTRIBUTE_NAME ,
# MAGIC     DATATYPE ,
# MAGIC     DICTIONARY_SIZE ,
# MAGIC     DICTIONARY_ISPAGEABLE ,
# MAGIC     DICTIONARY_ISRESIDENT ,
# MAGIC     DICTIONARY_TEMPERATURE ,
# MAGIC     DICTIONARY_LAST_ACCESSED
# MAGIC FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
# MAGIC ORDER BY [DICTIONARY_TEMPERATURE] DESC

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# # REFRAME Semantic Model

# CELL ********************

fabric.refresh_dataset(workspace=myworkspace, dataset=mydataset, refresh_type ="Full")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%dax {mydataset}
# MAGIC SELECT 
# MAGIC     MEASURE_GROUP_NAME,
# MAGIC     ATTRIBUTE_NAME ,
# MAGIC     DATATYPE ,
# MAGIC     DICTIONARY_SIZE ,
# MAGIC     DICTIONARY_ISPAGEABLE ,
# MAGIC     DICTIONARY_ISRESIDENT ,
# MAGIC     DICTIONARY_TEMPERATURE ,
# MAGIC     DICTIONARY_LAST_ACCESSED
# MAGIC FROM $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS 
# MAGIC ORDER BY [DICTIONARY_TEMPERATURE] DESC

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
