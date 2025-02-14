section Section1;
shared gold_dimvideos = let
  Source = Lakehouse.Contents(null){[workspaceId = "97dc8aaf-6f99-4fee-ae59-a4f47ec3c596"]}[Data]{[lakehouseId = "7753f722-3ed4-4d13-a8d7-a58129461435"]}[Data],
  #"Navigation 1" = Source{[Id = "gold_dimvideos", ItemKind = "Table"]}[Data],
  #"Choose columns" = Table.SelectColumns(#"Navigation 1", {"VideoSK", "VideoAK"}),
  #"Added custom" = Table.AddColumn(#"Choose columns", "VideoURL", each "https://www.youtube.com/watch?v=" & [VideoAK]),
  #"Added custom 1" = Table.AddColumn(#"Added custom", "ThumbNailURL", each "https://i.ytimg.com/vi/" & [VideoAK] & "/hqdefault.jpg"),
  #"Changed column type" = Table.TransformColumnTypes(#"Added custom 1", {{"VideoURL", type text}, {"ThumbNailURL", type text}})
in
  #"Changed column type";
