import networkx as nx
import geopandas as gpd
import os


def DrawGraph(path, path2, CNAME, imagename):
	gpd_input = gpd.read_file(path)
	utm_crs = gpd_input.estimate_utm_crs()
	gpd_input = gpd_input.to_crs(utm_crs)
	print(gpd_input.estimate_utm_crs())

	gpd_input['weight'] = gpd_input.geometry.length
	gpd_input.to_file(path)

	output_dir  = fr'./Data/{CNAME}/NewShape'
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	Ge = nx.read_shp(path)
	l=[x for x in Ge.edges()]

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
	nx.set_edge_attributes(Ge, imagename, "image_name")
	nx.set_edge_attributes(Ge, "segment_length", "weight")
	so_df = nx.to_pandas_edgelist(Ge)
	
	listLines = []
	for i in range(len(so_df)):
	    listLines.append(f' LINESTRING ({so_df["source"][i][0]} {so_df["source"][i][1]}, {so_df["target"][i][0]} {so_df["target"][i][1]})')
	so_df['geom'] = listLines
	
	gs = gpd.GeoSeries.from_wkt(so_df['geom'])
	gdf = gpd.GeoDataFrame(so_df, crs=utm_crs, geometry=gs)
	gdf = gdf.drop(columns=['source', 'target','geom','Wkt', 'Wkb', 'Json', 'ShpName'])
	gdf = gdf.to_crs("EPSG:4326")
	gdf.to_file(path2, driver="ESRI Shapefile")
	return gdf.to_json()
    