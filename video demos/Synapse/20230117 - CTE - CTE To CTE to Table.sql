WITH InternetSalesByProduct
AS
(
	SELECT 
		ProductKey,
		SUM(SalesAmount) InternetSales
	FROM dbo.InternetSales
	GROUP BY
		ProductKey
),
ResellerSalesByProduct
AS
(
	SELECT 
		ProductKey,
		SUM(Salesamount)ResellerSales
	FROM dbo.FactResellerSales r
	GROUP BY
		ProductKey
)
SELECT 
	p.EnglishProductName,
	COALESCE(r.ProductKey, i.ProductKey),
	r.ResellerSales,
	i.InternetSales,
	IIF(r.ResellerSales IS NOT NULL, r.ResellerSales/(r.ResellerSales + i.InternetSales),null) PctResellerSales,
	IIF(i.InternetSales IS NOT NULL, i.InternetSales/(r.ResellerSales + i.InternetSales),null) PctInternetSales,
	r.ResellerSales + i.InternetSales TotalSales
FROM ResellerSalesByProduct r
FULL OUTER JOIN InternetSalesByProduct i
	ON r.ProductKey = i.ProductKey	
INNER JOIN dbo.DimProduct p
	ON p.ProductKey = COALESCE(r.ProductKey, i.ProductKey)

