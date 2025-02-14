CREATE TABLE [dbo].[FactChannelStats] (

	[CaptureDateSK] date NULL, 
	[ChannelSK] int NULL, 
	[SubscriberCount] int NULL, 
	[ViewCount] int NULL, 
	[VideoCount] int NULL
);


GO
ALTER TABLE [dbo].[FactChannelStats] ADD CONSTRAINT FK_FactChannelStats_To_DimCalendar_On_CaptureDateSK FOREIGN KEY ([CaptureDateSK]) REFERENCES [dbo].[DimCalendar]([ActualDate]);
GO
ALTER TABLE [dbo].[FactChannelStats] ADD CONSTRAINT FK_FactChannelStats_To_DimChannel_On_ChannelSK FOREIGN KEY ([ChannelSK]) REFERENCES [dbo].[DimChannel]([ChannelSK]);