import fiona
from shapely.geometry import shape, GeometryCollection
from shapely.geometry import shape, LineString, Point, MultiLineString, MultiPoint
from shapely.ops import unary_union, split, snap, transform, nearest_points, linemerge
import shapely.ops
import itertools
import geopandas as gpd
import pyproj
import numpy as np
import pandas as pd



def find_intersections(json_local, filepath):
	features = json_local["features"]

	gc_roads = GeometryCollection([shape(feature["geometry"]) for feature in features])

	segments = []
	for g in unary_union(gc_roads).geoms:
		segments.extend(list(map(LineString, zip(g.coords[:-1], g.coords[1:]))))

	# PART 1: FINDING INTERSECTIONS
	pts_inter = []
	for i, seg in enumerate(segments):
		pts_inter.append(Point(seg.coords[0]))
		pts_inter.append(Point(seg.coords[1]))

		for j in range(i+1, len(segments)): # compare i segment to j segment
			if i == 0:
				pts_inter.append(Point(segments[j].coords[0]))
				pts_inter.append(Point(segments[j].coords[1]))

			if seg.distance(segments[j]) >0 and seg.distance(segments[j]) < 1:  # find unsnapped vertexes
				pt1, pt2 = nearest_points(seg, segments[j])
				pts_inter.append(pt1)

			if seg.intersects(segments[j]): # find intersections
				inter = seg.intersection(segments[j])        
				pts_inter.append(inter)


	gdf_inter = gpd.GeoDataFrame(geometry=pts_inter).drop_duplicates()
	gdf_inter = gdf_inter.reset_index(drop=True)
	gdf_inter.index.name='node_id'
	gdf_inter.geometry = gdf_inter.geometry.buffer(3)  # create buffers for intersections

	
	# drop vertex duplicates (before loop is not ideal - often adding the same vertex)
	gdf_inter_merged = gpd.GeoDataFrame(geometry=gpd.GeoSeries(gdf_inter.unary_union).explode(index_parts=False).reset_index(drop=True))
	gdf_inter_merged.geometry = gdf_inter_merged.geometry.buffer(3)
	gdf_inter_merged['geom'] = gdf_inter_merged.geometry.centroid
	print(len(gdf_inter_merged))
	
	# PART 2
	segments_id = []
	for i, segment in enumerate(segments):
		segments_id.append(i)

	gdf_segments = gpd.GeoDataFrame(geometry=segments).drop_duplicates()
	gdf_segments['edge_id'] = segments_id
	gdf_segments['length'] = gdf_segments.geometry.length
	gdf_segments = gdf_segments.loc[gdf_segments['length']  > 1]  # remove segments with length < 1

	intersection = gpd.sjoin(gdf_inter_merged, gdf_segments, how="left", predicate='intersects')

	grouped = intersection.groupby("edge_id")['geom'].apply(lambda x:  LineString(x.tolist()) if len(x.tolist()) > 1 else None)

	gdf_grouped = gpd.GeoDataFrame(grouped)
	gdf_grouped = gdf_grouped[gdf_grouped['geom'] != None]
	gdf_grouped.geometry = gdf_grouped['geom']


	geoms = [shape(feature) for feature in gdf_grouped.geometry.tolist()]
	lines = MultiLineString(geoms)



	new_lines = []
	for line in lines:
		points = list(line.coords)
		nPoints = len(points)

		lines_unsorted = []
		pt1_id = []
		pt2_id = []
		for i, p in enumerate(points):
			for j in range(i+1, len(points)):
				lines_unsorted.append(LineString([points[i], points[j]]))
				pt1_id.append(i)
				pt2_id.append(j)
		

		gdf_lines_sorted = gpd.GeoDataFrame(geometry=lines_unsorted).drop_duplicates()  # tworzenie gdf
		gdf_lines_sorted['node1_id'] = pt1_id
		gdf_lines_sorted['node2_id'] = pt2_id
		gdf_lines_sorted['length'] = gdf_lines_sorted.geometry.length
		gdf_lines_sorted = gdf_lines_sorted.sort_values('length').reset_index(drop=True)  # sortowanie na podstawie długość
		
		geometry_list = gdf_lines_sorted.geometry.tolist() # konwersja geometrii do listy
		id1_list = gdf_lines_sorted['node1_id'].tolist() # konwersja geometrii do listy
		id2_list = gdf_lines_sorted['node2_id'].tolist() # konwersja geometrii do listy

		row_lines_geometry = []
		row_lines_ids = []
		row_lines_geometry.append(geometry_list[0])   # wstawienie najkrótszego odcinka
		row_lines_ids.append(id1_list[0])   # wstawienie najkrótszego odcinka
		row_lines_ids.append(id2_list[0])   # wstawienie najkrótszego odcinka
		
		for i, geom in enumerate(geometry_list):  # iterowanie po odcinkach
			if i > (nPoints+1):
				break
			if i == 0:
				continue
			
			count_common_nodes = row_lines_ids.count(id1_list[i]) + row_lines_ids.count(id2_list[i])
			if count_common_nodes == 1:
				row_lines_geometry.append(geom)
				if id1_list[i] not in row_lines_ids:
					row_lines_ids.append(id1_list[i])
				if id2_list[i] not in row_lines_ids:
					row_lines_ids.append(id2_list[i])


		new_lines.extend(row_lines_geometry)
	


	gdf_new_lines = gpd.GeoDataFrame( geometry=new_lines).drop_duplicates()
	gdf_new_lines['length'] = gdf_new_lines.geometry.length
	gdf_new_lines.sort_values('length')
	gdf_new_lines = gdf_new_lines.loc[gdf_new_lines['length']  > 1]
	gdf_new_lines.to_file(filepath)
	
	
