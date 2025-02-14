CREATE TABLE [dbo].[DimVideo] (

	[VideoSK] int NOT NULL, 
	[ChannelSK] int NOT NULL, 
	[VideoAK] varchar(50) NULL, 
	[Title] varchar(150) NULL, 
	[Descr] varchar(5000) NULL, 
	[LiveStream] varchar(10) NULL, 
	[PusblishedDate] date NULL, 
	[Hosts] varchar(75) NULL, 
	[VideoURL] varchar(150) NULL, 
	[ThumbNailURL] varchar(150) NULL
);


GO
ALTER TABLE [dbo].[DimVideo] ADD CONSTRAINT PK_DimVideo_VideoSK primary key NONCLUSTERED ([VideoSK]);