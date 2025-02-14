-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "sqldatawarehouse"
-- META   },
-- META   "dependencies": {
-- META     "warehouse": {
-- META       "default_warehouse": "80b25592-a70f-4c06-ad79-fc373fbf734a",
-- META       "known_warehouses": [
-- META         {
-- META           "id": "80b25592-a70f-4c06-ad79-fc373fbf734a",
-- META           "type": "Datawarehouse"
-- META         },
-- META         {
-- META           "id": "f2f8dd4d-6236-4f98-9f2e-abbcbc7fa139",
-- META           "type": "Lakewarehouse"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

ALTER TABLE dbo.FactChannelStats
    DROP CONSTRAINT FK_FactChannelStats_To_DimCalendar_On_CaptureDateSK;

ALTER TABLE dbo.FactChannelStats
    DROP CONSTRAINT FK_FactChannelStats_To_DimChannel_On_ChannelSK

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DROP TABLE IF EXISTS dbo.DimChannel
GO
CREATE TABLE dbo.DimChannel
(
    ChannelSK int NOT NULL,
    ChannelAK varchar(50),
    PlayListID varchar(50),
    ChannelName varchar(75),
    CaptureDate date
)

ALTER TABLE DimChannel ADD CONSTRAINT PK_DimChannel_ChannelSK PRIMARY KEY NONCLUSTERED (ChannelSK) NOT ENFORCED;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DROP TABLE IF EXISTS dbo.DimVideo
GO
CREATE TABLE dbo.DimVideo
(
    VideoSK int NOT NULL,
    ChannelSK int NOT NULL,
    VideoAK varchar(50),
    Title varchar(150),
    Descr varchar(5000),
    LiveStream varchar(10),
    PusblishedDate date,
    Hosts varchar(75),
    VideoURL varchar(150),
    ThumbNailURL varchar(150)
)

ALTER TABLE DimVideo ADD CONSTRAINT PK_DimVideo_VideoSK PRIMARY KEY NONCLUSTERED (VideoSK) NOT ENFORCED;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

DROP TABLE IF EXISTS dbo.DimCalendar
GO
CREATE TABLE dbo.DimCalendar
(
    ActualDate date not null,
    [Year] int,
    MonthNum int,
    [MonthName] varchar(20),
    WeekDayName varchar(20),
    WeekDayNum int
)
GO
ALTER TABLE DimCalendar ADD CONSTRAINT PK_DimCalendar_ActualDate PRIMARY KEY NONCLUSTERED (ActualDate) NOT ENFORCED;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************


DROP TABLE IF EXISTS dbo.FactChannelStats
GO
CREATE TABLE dbo.FactChannelStats
(
    CaptureDateSK date,
    ChannelSK int,
    SubscriberCount int,
    ViewCount int,
    VideoCount int
)
GO

ALTER TABLE FactChannelStats
    ADD CONSTRAINT FK_FactChannelStats_To_DimCalendar_On_CaptureDateSK
        FOREIGN KEY  (CaptureDateSK)
            REFERENCES dbo.DimCalendar (ActualDate) NOT ENFORCED;

ALTER TABLE FactChannelStats
    ADD CONSTRAINT FK_FactChannelStats_To_DimChannel_On_ChannelSK
        FOREIGN KEY  (ChannelSK)
            REFERENCES dbo.DimChannel (ChannelSK) NOT ENFORCED;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

CREATE SCHEMA staging

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
