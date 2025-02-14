CREATE TABLE [dbo].[DimChannel] (

	[ChannelSK] int NOT NULL, 
	[ChannelAK] varchar(50) NULL, 
	[PlayListID] varchar(50) NULL, 
	[ChannelName] varchar(75) NULL, 
	[CaptureDate] date NULL
);


GO
ALTER TABLE [dbo].[DimChannel] ADD CONSTRAINT PK_DimChannel_ChannelSK primary key NONCLUSTERED ([ChannelSK]);