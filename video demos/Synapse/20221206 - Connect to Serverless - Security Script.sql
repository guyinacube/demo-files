CREATE MASTER KEY ENCRYPTION BY PASSWORD = '***************'
GO

CREATE DATABASE SCOPED CREDENTIAL [PowerBIMI]
WITH IDENTITY = 'Managed Identity'
GO


CREATE EXTERNAL DATA SOURCE PowerBIDS
WITH
  (  LOCATION = 'abfss://gold@leblancsynapsedlgen2.dfs.core.windows.net', --container names are case sensitive
    CREDENTIAL =  [PowerBIMI]
)
GO














CREATE LOGIN PowerBI WITH PASSWORD = '**************';
GO
CREATE USER PowerBI FROM LOGIN PowerBI
GO
ALTER ROLE db_datareader ADD  MEMBER PowerBI; 
GO

GRANT SELECT ON DIMPRODUCT TO PowerBI

GRANT CONTROL TO PowerBI
GRANT REFERENCES ON CREDENTIAL::[PowerBIMI] TO PowerBI

GO

CREATE VIEW DimProductwDS
AS
SELECT
    *
FROM
    OPENROWSET(
        BULK 'Delta/Dimension/Product/',
        data_source = 'PowerBIDS',
        FORMAT = 'PARQUET'
    ) AS [result]

GO

CREATE VIEW FactSaleswDS
AS
SELECT
    *
FROM
    OPENROWSET(
        BULK 'Delta/Fact/Sales/',
        data_source = 'PowerBIDS',
        FORMAT = 'PARQUET'
    ) AS [result]

GO



