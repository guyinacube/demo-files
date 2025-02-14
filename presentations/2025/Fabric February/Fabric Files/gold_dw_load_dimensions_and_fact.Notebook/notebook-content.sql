-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "sqldatawarehouse"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "7753f722-3ed4-4d13-a8d7-a58129461435",
-- META       "default_lakehouse_name": "YT_LakeHouse",
-- META       "default_lakehouse_workspace_id": "97dc8aaf-6f99-4fee-ae59-a4f47ec3c596"
-- META     },
-- META     "warehouse": {
-- META       "default_warehouse": "80b25592-a70f-4c06-ad79-fc373fbf734a",
-- META       "known_warehouses": [
-- META         {
-- META           "id": "80b25592-a70f-4c06-ad79-fc373fbf734a",
-- META           "type": "Datawarehouse"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

DECLARE 
    @ChannelSK int = (SELECT COALESCE(MAX(ChannelSK),0) FROM dbo.DimChannel dc)

SELECT 
    ROW_NUMBER() OVER(ORDER BY sc.ChannelName ASC)+@ChannelSK AS ChannelSK,
    sc.ChannelID ChannelAK,
    sc.PlayListID,
    sc.ChannelName,
    sc.CaptureDate
FROM YT_LakeHouse.dbo.silver_channels sc
LEFT OUTER JOIN dbo.DimChannel dc
    ON sc.ChannelID = dc.ChannelAK
WHERE  
    dc.ChannelAK IS NULL

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

CREATE PROC dbo.LoadDimChannel
AS
DECLARE 
    @ChannelSK int = (SELECT COALESCE(MAX(ChannelSK),0) FROM dbo.DimChannel dc)

INSERT INTO dbo.DimChannel
SELECT 
    ROW_NUMBER() OVER(ORDER BY sc.ChannelName ASC)+@ChannelSK AS ChannelSK,
    sc.ChannelID ChannelAK,
    sc.PlayListID,
    sc.ChannelName,
    sc.CaptureDate
FROM YT_LakeHouse.dbo.silver_channels sc
LEFT OUTER JOIN dbo.DimChannel dc
    ON sc.ChannelID = dc.ChannelAK
WHERE  
    dc.ChannelAK IS NULL

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DECLARE 
    @VideoSK int = (SELECT COALESCE(MAX(VideoSK),0) FROM dbo.DimVideo dv)

INSERT INTO dbo.DimVideo
SELECT 
    ROW_NUMBER() OVER(ORDER BY sv.VideoID ASC)+@VideoSK AS VideoSK,
    dc.ChannelSK,
    sv.VideoID,
    sv.Title, 
    sv.VideoDescr,
    sv.LiveStream,
    sv.PublishedDate,
    sv.Hosts,
    'https://www.youtube.com/watch?v=' + sv.VideoID VideoURL,
    'https://i.ytimg.com/vi/' + sv.VideoID + '/hqdefault.jpg' ThumbNailURL
FROM YT_LakeHouse.dbo.silver_videos sv
LEFT OUTER JOIN dbo.DimVideo dv
    ON sv.VideoID = dv.VideoAK
LEFT OUTER JOIN dbo.DimChannel dc
    ON sv.ChannelID = dc.ChannelAK
WHERE  
    dv.VideoAK IS NULL

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DELETE FROM dbo.DimCalendar;

DECLARE 
    @StartDate datetime = '12/1/2024',
    @EndDate datetime = CAST(GETDATE() AS DATE),
    @StartInt int,
    @EndInt int


SELECT
    @StartInt = CAST(@StartDate AS INT),
    @EndInt = CAST(@EndDate AS INT);

With Days
AS
(
    SELECT
        CAST(CAST(value as datetime) AS [DATE]) [Actual Date]
    FROM GENERATE_SERIES(@StartInt, @EndInt, 1)
)
INSERT INTO dbo.DimCalendar
SELECT 
    [Actual Date] DateKey,
    YEAR([Actual Date]) [Year],
    Month([Actual Date]) MonthNumber,
    DATENAME(MONTH, [Actual Date]) [Month],
    DATENAME(dw, [Actual Date]) [WeekDayName],
    DATEPART(dw, [Actual Date]) [WeekDayNum]
FROM Days

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DECLARE 
    @StartDate datetime = '12/1/2024',
    @EndDate datetime = CAST(GETDATE() AS DATE),
    @StartInt int,
    @EndInt int


SELECT
    @StartInt = CAST(@StartDate AS INT),
    @EndInt = CAST(@EndDate AS INT);

With Days
AS
(
    SELECT
        CAST(CAST(value as datetime) AS [DATE]) [Actual Date]
    FROM GENERATE_SERIES(@StartInt, @EndInt, 1)
)
SELECT 
    [Actual Date] DateKey,
    YEAR([Actual Date]) [Year],
    Month([Actual Date]) MonthNumber,
    DATENAME(MONTH, [Actual Date]) [Month],
    DATENAME(dw, [Actual Date]) [WeekDayName],
    DATEPART(dw, [Actual Date]) [WeekDayNum]
FROM Days

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DELETE FROM dbo.FactChannelStats;

INSERT INTO dbo.FactChannelStats
SELECT 
    dc.ActualDate CaptureDateSK,
    COALESCE(dcn.ChannelSK, -1),
    SubscriberCount,
    VideoCount,
    ViewCount
FROM YT_LakeHouse.dbo.silver_channelstats scs
LEFT OUTER JOIN dbo.DimCalendar dc
    ON scs.CaptureDate = dc.ActualDate
LEFT OUTER JOIN dbo.DimChannel dcn
    ON scs.ChannelID = dcn.ChannelAK

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
