DROP TABLE IF EXISTS junk.FactQuotaWithoutJunk
GO
DROP TABLE IF EXISTS junk.FactQuotaWithJunk
GO
DROP TABLE IF EXISTS junk.opsSalesQuota
GO
DROP TABLE IF EXISTS junk.opsScenario
GO
DROP TABLE IF EXISTS junk.opsChannel
GO
DROP TABLE IF EXISTS junk.DimStore
GO
DROP TABLE IF EXISTS junk.DimQuotaInfo
GO
DROP TABLE IF EXISTS junk.DimScenario
GO
DROP TABLE IF EXISTS junk.DimChannel
GO
DROP SCHEMA IF EXISTS junk
GO
CREATE SCHEMA junk
GO


CREATE TABLE junk.opsChannel
(
	ChannelLabel char(2) NOT NULL
		CONSTRAINT PK_opsChannel_ChannelLabel PRIMARY KEY,
	ChannelName  varchar(20) NOT NULL
)
GO

INSERT INTO junk.opsChannel
VALUES
('01', 'Store'),
('02', 'Online'),
('03', 'Catalog'),
('04', 'Reseller')
GO

CREATE TABLE junk.opsScenario
(
	ScenarioLabel char(2) NOT NULL
		CONSTRAINT PK_opsScenario_ScenarioLabel  PRIMARY KEY,
	ScenarioName varchar(20) NOT NULL
)
GO

INSERT INTO junk.opsScenario
VALUES
('01', 'Actual'),
('02', 'Budget'),
('03', 'Forecast')
GO


CREATE TABLE junk.opsSalesQuota
(
	QuotaID int identity(1,1)
		CONSTRAINT PK_opsSalesQuota_QuotaID PRIMARY KEY,
	StoreID int NOT NULL,
	ScenarioID char(2) NOT NULL,
	ChannelID char(2) NOT NULL,
	SalesQuota int NOT NULL,
	QuotaDate datetime NOT NULL
)
GO

INSERT INTO junk.opsSalesQuota(StoreID, ScenarioID, ChannelID, SalesQuota, QuotaDate)
VALUES
	(635,'03','03',50000, '1/1/2023'),
	(636,'02','03',75000, '1/1/2023'),
	(934,'03','02',75000, '1/1/2023'),
	(638,'03','04',100000, '1/1/2023'),
	(635,'02','02',50000, '2/1/2023'),
	(636,'03','01',75000, '2/1/2023'),
	(934,'01','04',1250000, '2/1/2023'),
	(638,'03','03',75000, '2/1/2023')
GO


SELECT * FROM junk.opsScenario
SELECT * FROM junk.opsChannel
SELECT * FROM junk.opsSalesQuota
GO

CREATE TABLE junk.DimStore
(
	StoreSK int NOT NULL
		CONSTRAINT PK_DimStore_StoreKey PRIMARY KEY,
	StoreAK int NOT NULL,
	StoreType varchar(10) NOT NULL,
	StoreName varchar(50) NOT NULL,
	OpenDate datetime NOT NULL,
	ZipCode int NOT NULL,
	StorePhone varchar(15) NOT NULL
)
GO



CREATE TABLE junk.DimChannel
(
	ChannelSK int IDENTITY(1,1) NOT NULL
		CONSTRAINT PK_ChannelInfo_ChannelSK PRIMARY KEY,
	ChannelLabel char(2) NOT NULL,
	ChannelName  varchar(20) NOT NULL
)
GO

CREATE TABLE junk.DimScenario
(
	ScenarioSK int IDENTITY(1,1) NOT NULL
		CONSTRAINT PK_DimScenario_ScenarioSK PRIMARY KEY,
	ScenarioLabel char(2) NOT NULL,
	ScenarioName varchar(20) NOT NULL
)
GO

INSERT INTO junk.DimChannel
SELECT 
	c.ChannelLabel ChannelAK,
	c.ChannelName
FROM junk.opsChannel c
GO

INSERT INTO junk.DimScenario
SELECT 
	s.ScenarioLabel ScenarioAK,
	s.ScenarioName
FROM junk.opsScenario s
GO

INSERT INTO junk.DimStore
VALUES
	(1, 635, 'Store', 'Contoso Thornton Store', '2003-04-29 00:00:00.000', 87001, '333-555-0173'),
	(2, 636, 'Booth', 'Contoso Manitowoc Store', '2004-04-27 00:00:00.000', 54019, '714-555-0138'),
	(3, 934, 'Store', 'Contoso Richardson Store', '2003-03-31 00:00:00.000', 75201, '845-555-0184'),
	(4, 638, 'Reseller', 'Contoso Desoto Store', '2003-02-01 00:00:00.000', 75208, '935-555-0116')
GO

CREATE TABLE junk.FactQuotaWithoutJunk
(
	StoreSK int NOT NULL
		CONSTRAINT FK_FactQuotaWithoutJunk_To_DimStore_On_StoreSK
			FOREIGN KEY (StoreSK)
				REFERENCES junk.DimStore (StoreSK),
	ScenarioSK int NOT NULL
		CONSTRAINT FK_FactQuotaWithoutJunk_To_DimScenario_On_ScenarioSK
			FOREIGN KEY (ScenarioSK)
				REFERENCES junk.DimScenario(ScenarioSK),
	ChannelSK int NOT NULL
		CONSTRAINT FK_FactQuotaWithoutJunk_To_DimChannel_On_ChannelSK
			FOREIGN KEY (ChannelSK)
				REFERENCES junk.DimChannel (ChannelSK),
	QuotaDate datetime NOT NULL,
	SalesQuota int NOT NULL
)
GO

INSERT INTO junk.FactQuotaWithoutJunk
SELECT 
	s.StoreSK,
	sc.ScenarioSK,
	c.ChannelSK,
	sq.QuotaDate,
	sq.SalesQuota
FROM junk.opsSalesQuota sq
LEFT OUTER JOIN junk.DimChannel c
	ON	sq.ChannelID = c.ChannelLabel 
LEFT OUTER JOIN junk.DimScenario sc
	ON	sq.ScenarioID = sc.ScenarioLabel
LEFT OUTER JOIN junk.DimStore s
	ON sq.StoreID = s.StoreAK

SELECT * FROM junk.FactQuotaWithoutJunkl

/*Lets Create the Junk Dimension*/
SELECT 
	ROW_NUMBER() OVER(ORDER BY c.ChannelLabel, s.ScenarioLabel) AS QuotaInfoKey,
	c.ChannelLabel ChannelAK,
	c.ChannelName,
	s.ScenarioLabel ScenarioAK,
	s.ScenarioName
FROM junk.opsChannel c
CROSS JOIN junk.opsScenario s
GO

/*OPTION TWO*/
;WITH quotaInfo 
AS
(
	SELECT DISTINCT
		c.ChannelLabel ChannelAK,
		c.ChannelName,
		s.ScenarioLabel ScenarioAK,
		s.ScenarioName
	FROM junk.opsSalesQuota sq
	LEFT OUTER JOIN junk.opsChannel c
		ON sq.ChannelID = c.ChannelLabel
	LEFT OUTER JOIN junk.opsScenario s
		ON sq.ScenarioID = s.ScenarioLabel
)
SELECT
	ROW_NUMBER() OVER(ORDER BY ChannelAK, ScenarioAK) AS QuotaInfoKey,
	*
FROM quotaInfo
GO

CREATE TABLE junk.DimQuotaInfo
(
	QuotaInfoSK int IDENTITY(1,1) NOT NULL
		CONSTRAINT PK_DimQuotaInfo_QuotaInfoSK PRIMARY KEY,
	ScenarioLabel char(2) NOT NULL,
	ScenarioName varchar(20) NOT NULL,
	ChannelLabel char(2) NOT NULL,
	ChannelName  varchar(20) NOT NULL
)
GO


INSERT INTO junk.DimQuotaInfo
SELECT 
	s.ScenarioLabel ScenarioAK,
	s.ScenarioName,
	c.ChannelLabel ChannelAK,
	c.ChannelName
FROM junk.opsChannel c
CROSS JOIN junk.opsScenario s
GO

CREATE TABLE junk.FactQuotaWithJunk
(
	StoreSK int NOT NULL
		CONSTRAINT FK_FactQuotaWithJunk_To_DimStore_On_StoreSK
			FOREIGN KEY (StoreSK)
				REFERENCES junk.DimStore (StoreSK),
	QuotaInfoSK int NOT NULL
		CONSTRAINT FK_FactQuotaWithJunk_To_DimQuoteInfo_On_QuotaInfoSK
			FOREIGN KEY (QuotaInfoSK)
				REFERENCES junk.DimQuotaInfo (QuotaInfoSK),
	QuotaDate datetime NOT NULL,
	SalesQuota int NOT NULL
)
GO



INSERT INTO junk.FactQuotaWithJunk
SELECT 
	s.StoreSK,
	qi.QuotaInfoSK,
	sq.QuotaDate,
	sq.SalesQuota
FROM junk.opsSalesQuota sq
LEFT OUTER JOIN junk.DimQuotaInfo qi
	ON	sq.ChannelID = qi.ChannelLabel AND
		sq.ScenarioID = qi.ScenarioLabel
LEFT OUTER JOIN junk.DimStore s
	ON sq.StoreID = s.StoreAK


	