from shapely.geometry import shape, LineString, Point
from shapely.ops import unary_union, split, snap, transform, nearest_points, linemerge
import shapely.ops
import itertools
import geopandas as gpd
import matplotlib.pyplot as plt
import pyproj
    
def divide_into_segments(geoms):
    res = unary_union(geoms)
    segments = []
    for g in geoms:
        segments.extend(list(map(LineString, zip(g.coords[:-1], g.coords[1:]))))
    
    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('EPSG:32618')
    project = pyproj.Transformer.from_crs(wgs84, utm).transform
    res = transform(project, res)
    print(res)

    segments_utm = []
    for s in segments:
        segments_utm.append(transform(project, s))


    

    # PART FOR FIDNING INTERSECTIONS
    pts_inter = []
    segments2 = []
    segs = []
    for seg1,seg2 in itertools.combinations(segments_utm,2):
        # print(seg1)
        # print(seg2)
        # seg1_buff = seg1.buffer(0.1)
        # seg2_buff = seg2.buffer(0.5)

        segs.append(seg1)
        segs.append(seg2)
        
        
        # if seg1.distance(seg2) < 0.1:

        if seg1.distance(seg2) >0 and seg1.distance(seg2) < 3:
            print(seg1.distance(seg2))
            pt1, pt2 = nearest_points(seg1, seg2)
            
            print("ADDED 1: ", pt1)         
            print("SNAP")
            print(pt1, pt2)
            if Point(seg2.coords[0]).distance(pt1) < Point(seg2.coords[1]).distance(pt1):
                snapped_seg2 = LineString([pt1, Point(seg2.coords[1])])
            else:
                snapped_seg2 = LineString([Point(seg2.coords[0]), pt1])
            # seg1 = unary_union(seg1)
            shapely.ops.snap(seg2, pt1, 5)
            pts_inter.append(pt1)  
            # segs.append(snapped_seg2)
            
        # print(seg1.distance(seg2))

        if seg1.intersects(seg2):
            inter = seg1.intersection(seg2)        
            pts_inter.append(inter.centroid)
            print("ADDED 2: ", inter)
            # segs.append(seg1)
            # segs.append(seg1)
            
    merged_lines = unary_union(segs)
    inters = []
    for p in pts_inter:
        inter = p.buffer(0.5).intersection(merged_lines)
        inters.append(inter.centroid)

    # print("INTERS")
    # print(inters)
    # inters_gdf = gpd.GeoDataFrame(crs='epsg:32618', geometry=segs+inters)
    # inters_gdf.to_crs(crs=4326)
    # print(inters_gdf)
    # inters_gdf.plot()
    # plt.show()

    inters_union = unary_union(inters)

    
    # segs_gdf = gpd.GeoDataFrame(crs='epsg:32618', geometry=segs+pts_inter)
    # segs_gdf.to_crs(crs=4326)
    # print(segs_gdf)
    # segs_gdf.plot()
    # plt.show()

    inter_gdf = gpd.GeoDataFrame(crs='epsg:32618', geometry=pts_inter)
    print(inter_gdf)
    inter_gdf.to_crs(crs=4326)
    inter_gdf.plot()
    plt.show()
    n = len(pts_inter)
    print("LEN", n)
    snapped = [] 
    if n > 0:
        pts_union = unary_union(pts_inter)
        print("UNION", pts_union)
        split_line = split(merged_lines, pts_union.buffer(0.1))
        for l in split_line:
            segments2.append(l)

        # taken = [False] * n
        # max_dist_snapp = 3
        # for i in range(n):
            
            # if not taken[i]:
            #     print(i)
            #     count = 1
            #     point = pts_inter[i]
            #     taken[i] = True
            #     for j in range(i+1, n):
            #         print("DIST: ", pts_inter[i].distance(pts_inter[j]))
            #         if pts_inter[i].distance(pts_inter[j]) < max_dist_snapp:
            #             point = pts_inter[i]
            #             print("SNAPPED")
            #             taken[j] = True

            #     snapped.append(point)
        # pts_inter_copy = 
        # for point in pts_inter:
        #     p1, p2 = nearest_points()
        # split_line = split(res, snap(pts_union, res, 3))

        
           
    else:
        segments2 = segments_utm

    

    # print(segments)
    # print("LEN segments", len(segments))
    gdf = gpd.GeoDataFrame(crs='epsg:32618', geometry=segments2)
    # gdf.plot()
    # gdf = gdf.to_crs(crs=2180)
    # print(gdf)
    # for index, row in gdf.iterrows():
    #     tmp_gdf = gdf.copy()
    #     # tmp_gdf['geometry'].to_crs(crs=2180)
    #     tmp_gdf['distance'] = tmp_gdf.distance(row['geometry'])
    #     print(tmp_gdf['distance'])
    #     closest_geom = list(tmp_gdf.sort_values('distance')['geometry'])[1]
    #     print(closest_geom)
    #     # I took 1 because index 0 would be the row itself
    #     snapped_geom = snap(row['geometry'], closest_geom, 3)
    #     gdf.loc[index, 'geometry'] = snapped_geom

    # print(gdf)
    # gdf = gdf.to_crs('epsg:4326')
    # print("LEN GDF: ", len(gdf.index))
    
    


    project = pyproj.Transformer.from_crs(utm, wgs84).transform
    res = transform(project, res)
    results = []
    for s in segments2:
        # if s.length < 0.1:
        #     continue
        results.append(transform(project, s))

    return results, gdf