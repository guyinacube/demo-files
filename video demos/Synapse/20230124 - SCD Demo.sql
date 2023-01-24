DROP TABLE IF EXISTS ops.Product
GO
DROP TABLE IF EXISTS dw.DimProduct
GO
DROP SCHEMA IF EXISTS dw
GO
DROP SCHEMA IF EXISTS ops
GO
CREATE SCHEMA ops
GO
CREATE SCHEMA dw
GO


CREATE TABLE ops.Product
(
    ProductNumber varchar(50) Primary key,
    ProductName varchar(100),
    Color varchar(30),
    ListPrice decimal(12,2)
)
GO

INSERT INTO ops.Product(ProductNumber, ProductName, Color, ListPrice)
VALUES
	('BI-1234', 'Bike One', 'Black', 100),
	('BI-5679', 'Bike Two', 'Red', 75),
	('SB-123', 'Skate Board One', 'Multi', 30),
	('SB-456', 'Skate Board Two', 'Orange', 65),
	('SB-789', 'Skate Board Three', 'Pink', 25)
GO
SELECT *
FROM ops.Product
GO


CREATE TABLE dw.DimProduct
(
	ProductSK int identity(1,1),
		CONSTRAINT PK_DimProduct_ProductSK PRIMARY KEY (ProductSK),
	ProductAK varchar(50),
    ProductName varchar(100),
    Color varchar(30),
    ListPrice decimal(12,2),
	EffectiveDate datetime,
	ExpirationDate datetime,
	IsActive bit
)
GO


/***********Initialize the Dimension**********************/
MERGE dw.DimProduct dp
USING ops.Product p        
	ON p.ProductNumber = dp.ProductAK
WHEN NOT MATCHED THEN
	INSERT (ProductAK, ProductName, Color, ListPrice, EffectiveDate, ExpirationDate, IsActive)
	VALUES (p.ProductNumber, p.ProductName, p.Color, p.ListPrice, '1/3/2023',NULL, 1);
GO

SELECT * 
FROM dw.DimProduct

/***********Type 0**********************/
UPDATE ops.Product
SET 
	ListPrice = 150
WHERE 
	ProductNumber = 'BI-5679'
/****NOTHING HAPPENS********************/


SELECT *
FROM ops.Product
WHERE 
	ProductNumber = 'BI-5679'
GO
SELECT *
FROM dw.DimProduct
WHERE 
	ProductAK = 'BI-5679'
GO

/***********Type 1**********************/


MERGE dw.DimProduct dp
USING ops.Product p        
	ON p.ProductNumber = dp.ProductAK
WHEN NOT MATCHED THEN
	INSERT (ProductAK, ProductName, Color, ListPrice, EffectiveDate, ExpirationDate, IsActive)
	VALUES (p.ProductNumber, p.ProductName, p.Color, p.ListPrice, '1/3/2023',NULL, 1)
WHEN MATCHED 
	AND (dp.ListPrice <> p.ListPrice) THEN
	UPDATE
		SET dp.ListPrice = p.ListPrice;
GO

SELECT *
FROM dw.DimProduct
WHERE 
	ProductAK = 'BI-5679'
GO
/***********Type 2**********************/
UPDATE ops.Product
SET 
	ListPrice = 100
WHERE 
	ProductNumber = 'BI-5679'

--https://www.sqlservercentral.com/blogs/handling-type-ii-dimension-with-the-merge-statement
INSERT INTO dw.DimProduct(ProductAK, ProductName, Color, ListPrice, EffectiveDate, IsActive)
SELECT 
	ProductNumber, ProductName, Color, ListPrice, EffectiveDate, 1
FROM
(
	MERGE dw.DimProduct dp
	USING ops.Product p        
		ON p.ProductNumber = dp.ProductAK
	WHEN NOT MATCHED THEN
		INSERT (ProductAK, ProductName, Color, ListPrice, EffectiveDate, ExpirationDate, IsActive)
		VALUES (p.ProductNumber, p.ProductName, p.Color, p.ListPrice, '1/3/2023',NULL, 1)
	WHEN MATCHED 
		AND (dp.ListPrice <> p.ListPrice)
		AND ExpirationDate IS NULL THEN
		UPDATE
			SET 
				dp.IsActive = 0,
				dp.ExpirationDate = CONVERT(DATETIME, GETDATE(), 101)
	OUTPUT $Action MergeAction, 
	p.ProductNumber, p.ProductName, p.Color, p.ListPrice, CONVERT(DATETIME, GETDATE(), 101) EffectiveDate, 1 IsActive
) MergeOutput
WHERE
	MergeAction = 'Update';
GO

SELECT *
FROM dw.DimProduct
WHERE 
	ProductAK = 'BI-5679'
