def DrawGraph(path, path2, path3):
    Gr = nx.read_shp(path)
    pos = {k: v for k,v in enumerate(Gr.nodes())}
    X = nx.Graph()
    X.add_nodes_from(pos.keys())
    Ge = nx.read_shp(path2)
    l=[x for x in Ge.edges()]
    edg=[tuple(k for k,v in pos.items() if v in sl) for sl in l]

    oidlista = []
    for n in Ge.edges():
        t = list(n)
        oid = Ge.edges[t]['weight']
        if oid != 0:
            oidlista.append(oid)
    
    ed_cen = nx.edge_betweenness_centrality(Ge, weight = 'weight') 
    copiedd = dict.fromkeys(ed_cen.keys())
    dictcopiedd = dict(zip(copiedd, oidlista))
    nx.set_edge_attributes(Ge, dictcopiedd, "weight")
    
    so_ed_cen = nx.edge_betweenness_centrality(Ge, weight = 'weight')
    so_ed_cen_2 = nx.edge_betweenness_centrality(Ge)
    nx.set_edge_attributes(Ge, so_ed_cen, "bet_w")
    nx.set_edge_attributes(Ge, so_ed_cen_2, "bet")
    
    so_df = nx.to_pandas_edgelist(Ge)
    source = list(so_df["source"])
    target = list(so_df["target"])
    ed_cen_sub = nx.edge_betweenness_centrality_subset(Ge, sources = source, targets = target, normalized=True)
    ed_cen_sub_2 = nx.edge_betweenness_centrality_subset(Ge, sources = source, targets = target, normalized=True, weight = "weight")
    nx.set_edge_attributes(Ge, ed_cen_sub, "bet_cen")
    nx.set_edge_attributes(Ge, ed_cen_sub_2, "bet_cen_w")
    so_df = nx.to_pandas_edgelist(Ge)
    so_df.to_csv(r'./Data/Priene_dotestow/out_wgs/New Shape/PrieneEBC/dataframe_Priene.csv')
        
    crs = {'init':'epsg:4326'}
    
    listLines = []
    for i in range(len(so_df)):
        listLines.append(f' LINESTRING ({so_df["source"][i][0]} {so_df["source"][i][1]}, {so_df["target"][i][0]} {so_df["target"][i][1]})')
    so_df['geom'] = listLines
    
    gs = gpd.GeoSeries.from_wkt(so_df['geom'])
    gdf = gpd.GeoDataFrame(so_df, crs=crs, geometry=gs)
    gdf = gdf.drop(columns=['source', 'target','geom','Wkt', 'Wkb', 'Json', 'ShpName'])
    gdf.to_file(path3, driver="ESRI Shapefile")
    
    
path_dest = (r'./Data/Priene_dotestow/out_wgs/New Shape/nodes.shp')
path_dest2 = (r'./Data/Priene_dotestow/out_wgs/New Shape/edges.shp')
path_dest3 = (r'./Data/Priene_dotestow/out_wgs/New Shape/PrieneEBC/output_priene.shp')
DrawGraph(path_dest, path_dest2, path_dest3)