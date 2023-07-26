import networkx as nx

from pprint import pprint

import geopandas as gpd
from shapely.geometry import Point, LineString
from ShapefileToNetwork.main.convertor import GraphConvertor
import os

import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors




def DrawGraph(path, path2, path3, CNAME, imagename):
    input_file  =  f'./Data/wgs_{CNAME}.shp'
    # output_dir  = f'./Data/{CNAME}/out_wgs'
    output_dir  = f'./Data/{CNAME}'
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    graph_convertor_obj = GraphConvertor.GraphConvertor(input_file, output_dir)
    network = graph_convertor_obj.graph_convertor()
    positions = graph_convertor_obj.positions
    
    Gr = nx.read_shp(path)
    pos = {k: v for k,v in enumerate(Gr.nodes())}
    X = nx.Graph() #Empty graph
    X.add_nodes_from(pos.keys()) #Add nodes preserving coordinates
    Ge = nx.read_shp(path2)
    l=[x for x in Ge.edges()]
    edg=[tuple(k for k,v in pos.items() if v in sl) for sl in l] #Map the G.edges start and endpoints onto pos
    # plt.figure(figsize=(12,8))
    # print('pos',pos) - to jest słownik z pozycjami w taki sposób: {0: (27.295720059, 37.659473768), 
    # 1: (27.295720059, 37.659736485), 2: (27.296164021, 37.659473545), 3: (27.295283333, 37.659473985), 4: (27.295720059, 37.66018761)}
    nx.draw_networkx_nodes(X,pos,node_size=10,node_color='r')
    edg2 = []
    for i in edg:
        if len(i) == 2:
            edg2.append(i)
    X.add_edges_from(edg2)
    nx.draw_networkx_edges(X,pos)
    print('Number of nodes:', len(X.nodes))
    print('Number of edges:', len(X.edges))


    #list with weight of distances
    oidlista = []
    for n in Ge.edges():
        t = list(n)
        oid = Ge.edges[t]['weight']
        if oid != 0:
            oidlista.append(oid)
    
    # ed_cen = nx.edge_betweenness_centrality(X)
    ed_cen = nx.edge_betweenness_centrality(X, weight = 'weight')
    copiedd = dict.fromkeys(ed_cen.keys())
    dictcopiedd = dict(zip(copiedd, oidlista))
    nx.set_edge_attributes(X, dictcopiedd, "weight")
    # for d in (dictcopiedd.items()):
    #     print(d[0], d[1])
    # ed_cen = nx.edge_betweenness_centrality(X)
    ed_cen = nx.edge_betweenness_centrality(X, weight = 'weight')
    nx.set_edge_attributes(X, ed_cen, "betweenness")
    # for e in (ed_cen.items()):
    #     print(e[0], e[1])
    edgecolornew = []
    edgecolor = list(ed_cen.values())
    for i in edgecolor:
        edgecolornew.append(i)
    # plt.figure(figsize=(15,8))
    edges = nx.draw_networkx_edges(X, pos, edge_cmap=plt.cm.plasma, width = 3,
                                   edge_color=edgecolornew,
                                   edgelist=list(ed_cen.keys()), arrows=None)
    edges.set_norm(mcolors.SymLogNorm(linthresh=0.1))
    nodes = nx.draw_networkx_nodes(X, pos, node_size=2)
    # plt.title("Edge Betweenness Centrality")
    # plt.colorbar(edges)
    # ax = plt.axis()
    # plt.show()
    
    
    listAtttr = []
    for n in X.edges():
        t = list(n)
        atttr = X.edges[t]['betweenness']
        listAtttr.append(atttr)
    # print(listAtttr)
    
    
    for n in X.edges():
        t = list(n)
        atttr = X.edges[t]['betweenness']
        atttr2 = X.edges[t]['weight']
        # print(atttr)
        # print(atttr2)

    nEdges = []
    for e in X.edges():
        t = list(e)
        newPos = [positions[t[0]], positions[t[1]]]
        nEdges.append(newPos)
        
    X2 = nx.Graph()    
    X2.add_edges_from(nEdges)
    ed_cen2 = nx.edge_betweenness_centrality(X2)

    copiedd2 = dict.fromkeys(ed_cen2.keys())
    dictcopiedd2 = dict(zip(copiedd2, oidlista))
    nx.set_edge_attributes(X2, dictcopiedd2, "weight")
    
    copiedd3 = dict.fromkeys(ed_cen2.keys())
    dictcopiedd3 = dict(zip(copiedd3, listAtttr))
    nx.set_edge_attributes(X2, dictcopiedd3, "betweenness")

    for n in X2.edges():
        t = list(n)
        atr = X2.edges[t]['betweenness']
        atr2 = X2.edges[t]['weight']
    
    
    # Write to shp
    df = nx.to_pandas_edgelist(X2)
    # print(df)
    sourcels = list(df["source"])
    targetls = list(df["target"])
    ed_cen_sub = nx.edge_betweenness_centrality_subset(X2, sources = sourcels, targets = targetls, normalized=True, weight = "weight")
    # print(ed_cen_sub)
    nx.set_edge_attributes(X2, ed_cen_sub, "betweenness2")
    nx.set_edge_attributes(X2, imagename, "image_name")
    df = nx.to_pandas_edgelist(X2)
    # for e in (ed_cen_sub.items()):
    #     print(e[0], e[1])
        
    # crs = {'init':'epsg:4326'}
    
    listLines = []
    # for i in range(len(df)):
    #     listLine = []
    #     listLine.append(df['source'][i])
    #     listLine.append(df['target'][i])
    #     listLines.append(listLine)
    for i in range(len(df)):
        listLines.append(f' LINESTRING ({df["source"][i][0]} {df["source"][i][1]}, {df["target"][i][0]} {df["target"][i][1]})')
    df['geom'] = listLines
    # print(listLines)
    

    
    # geometry = [LineString(p) for p in listLines]
    # gdf = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
    # gdf.set_geometry(gdf['geometry'], inplace=True, crs=crs)
    # gdf.to_file(path3, driver="ESRI Shapefile")
    gs = gpd.GeoSeries.from_wkt(df['geom'])
    gdf = gpd.GeoDataFrame(df, crs='epsg:4326', geometry=gs)
    gdf =gdf.drop(columns=['source', 'target','geom'])
#     gdf.to_file(path3, driver="ESRI Shapefile")
    gdf.to_file(fr'./Data/{CNAME}/NewShape/ebc_{CNAME}.shp', driver="ESRI Shapefile")

    return gdf.to_json()
    
# path_dest = (fr'./Data/{CNAME}_dotestow/out_wgs/NewShape/nodes.shp')
# path_dest2 = (fr'./Data/{CNAME}_dotestow/out_wgs/NewShape/edges.shp')
# path_dest3 = (fr'./Data/{CNAME}_dotestow/out_wgs/NewShape/{CNAME}EBC/ebc_{CNAME}.shp')
# DrawGraph(path_dest, path_dest2, path_dest3)