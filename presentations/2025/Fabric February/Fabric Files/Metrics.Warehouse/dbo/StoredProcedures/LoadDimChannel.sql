CREATE PROC dbo.LoadDimChannel
AS
DECLARE 
    @ChannelSK int = (SELECT COALESCE(MAX(ChannelSK),0) FROM dbo.DimChannel dc)

INSERT INTO dbo.DimChannel
SELECT 
    ROW_NUMBER() OVER(ORDER BY sc.ChannelName ASC)+@ChannelSK AS ChannelSK,
    sc.ChannelID ChannelAK,
    sc.PlayListID,
    sc.ChannelName,
    sc.CaptureDate
FROM YT_LakeHouse.dbo.silver_channels sc
LEFT OUTER JOIN dbo.DimChannel dc
    ON sc.ChannelID = dc.ChannelAK
WHERE  
    dc.ChannelAK IS NULL