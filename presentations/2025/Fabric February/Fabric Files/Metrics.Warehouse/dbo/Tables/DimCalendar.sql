CREATE TABLE [dbo].[DimCalendar] (

	[ActualDate] date NOT NULL, 
	[Year] int NULL, 
	[MonthNum] int NULL, 
	[MonthName] varchar(20) NULL, 
	[WeekDayName] varchar(20) NULL, 
	[WeekDayNum] int NULL
);


GO
ALTER TABLE [dbo].[DimCalendar] ADD CONSTRAINT PK_DimCalendar_ActualDate primary key NONCLUSTERED ([ActualDate]);