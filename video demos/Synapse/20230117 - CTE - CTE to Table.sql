WITH SalesByEmployeeAndYear (SalesId,CustomerKey, OrderYear, SalesAmount)
AS
(
	SELECT 
		fas.SalesId,
		fas.CustomerKey,
		YEAR(fas.OrderDate),
		fas.SalesAmount
	FROM
	FactInternetSales fas
	--GROUP BY 
	--	fas.CustomerKey,
	--	YEAR(fas.OrderDate)
)
SELECT 
	c.EmailAddress,
	sbey.OrderYear,
	SUM(sbey.SalesAmount) AnnualSales,
	COUNT(sbey.SalesID) NumOfSales
FROM SalesByEmployeeAndYear sbey
INNER JOIN DimCustomer c
	ON sbey.CustomerKey = c.CustomerKey
GROUP BY
	c.EmailAddress,
	sbey.OrderYear
	 