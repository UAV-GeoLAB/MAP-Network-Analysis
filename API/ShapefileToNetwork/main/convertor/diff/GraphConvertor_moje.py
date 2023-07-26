from shapely.geometry import shape, LineString, Point
from shapely.ops import unary_union, split, snap, transform
import geopandas as gpd
import fiona
import networkx as nx
import itertools
from haversine import haversine
from .GraphSimplify import GraphSimplify
from .MultiDiGraphConvertor import MultiDiToSimple
from functools import partial
import pyproj


class GraphConvertor:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.positions = None

    '''
        @input:     The path of the shapefile which need to be converted to network
        @output:    Returns the MultiDigraph created from the shapefile

        This function read the shapefile of the road network and convert it into graph by iterating through the lat, lon
        from the shapefile.
    '''

    def shape_convertor(self):
        geoms = [shape(feature['geometry']) for feature in fiona.open(self.input_file)]
        

        res = unary_union(geoms)
        
        G = nx.MultiDiGraph()
        
        # print('res: ', res)
        # print('res: ', res.boundary)
        # print("halo")

        # from shapely.ops import split
        # splitted = split(res, res.boundary)
        # print(splitted)

        

        segments = []
        for g in geoms:
            segments.extend(list(map(LineString, zip(g.coords[:-1], g.coords[1:]))))
        

        # PART FOR FIDNING INTERSECTIONS
        pts_inter = []
        segments2 = []
        for seg1,seg2 in itertools.combinations(segments,2):
            if seg1.crosses(seg2):
                inter = seg1.intersection(seg2)        
                pts_inter.append(inter)
                
                # seg1.split(inter)
                # seg2.split(inter)
            #     splitted_lines = split(seg1, inter)
            #     print(seg1)
            #     print('splitted_lines: ', seg1.difference(inter.buffer(1e-13)))
            #     split_lines1 = seg1.difference(inter)
            #     split_lines2 = seg2.difference(inter)
            #     for line in split_lines1:
            #         segments2.extend([line])
            #         print(line)
            #     for line in split_lines2:
            #         print(line)
            #         segments2.extend([line])
            # #     # segments2.extend(list(map(LineString, zip(split_lines1.coords[:-1], split_lines1.coords[1:]))))
            # #     # segments2.extend(list(map(LineString, zip(split_lines2.coords[:-1], split_lines2.coords[1:]))))
            # else:
            #     segments2.extend([seg1, seg2])
        # if len(pts_inter) > 0:
        #     i = 0
        #     for s in segments:
        #         diff = s.difference(pts_inter[i].buffer(1e-13))
        #         if diff.geom_type == 'MultiLineString':
        #             for line in diff:
        #                 segments2.extend([line])
        #         elif diff.geom_type == 'LineString':
        #             segments2.append(diff)
        # print("SEGMENTS 2: ", len(segments2))
        if len(pts_inter) > 0:
            pts_union = unary_union(pts_inter)
            split_line = split(res, snap(pts_union, res, 3))
            for l in split_line:
                segments2.append(l)
               
        else:
            segments2 = segments
        
        for line in segments2:
            for seg_start, seg_end in zip(list(line.coords), list(line.coords)[1:]):
                start1 = (round(seg_start[0], 6), round(seg_start[1], 6))
                end1 = (round(seg_end[0], 6), round(seg_end[1], 6))
                
                # print("start: ", start1)
                # print("end: ", end1)
                
                # print("distance", haversine(start, end, unit='m'))

                project = partial(
                    pyproj.transform,
                    pyproj.Proj('EPSG:4326'),
                    pyproj.Proj('EPSG:32633')
                )

                start = (start1[1], start1[0])
                end = (end1[1], end1[0])
                p1 = Point(start1)
                p2 = Point(end1)
                line1 = LineString([p1, p2])
                line2 = transform(project, line1)

                G.add_edge(start1, end1, weight=line2.length)

                # print(str(line2.length) + " meters")

        return G

    '''
        @input:     The Graph and the path

        This function read the Graph, iterate over the list of nodes in the graph and save it into file defined by path
    '''

    def create_vertex_file(self, g):
        vertex = g.nodes
        output = open(self.output_dir + '/vertex.csv', 'w')
        output.write('Unique Id; Longitude; Latitude\n')

        count = 1
        for v in vertex:
            output.write(str(count) + ';' + str(round(v[0], 6)) + ';' + str(round(v[1], 6)) + '\n')
            count += 1

    '''
        @input:     The Graph and directory

        This function writes the graph in form of shape file to the given directory
    '''

    def create_edges_vertex_shape(self, g):
        nx.write_shp(g, self.output_dir + '/NewShape/')

    '''
        @input:     The Graph and the path

        This function iterate over the edges of the graph and write it into the file defined by the path
    '''

    def create_edges_file(self, g):
        output = open(self.output_dir + '/edges.csv', 'w')
        output.write('Starting Coordinate; End Coordinate; True Distance(m) \n')

        for edge in g.edges:
            distance = g.get_edge_data(edge[0], edge[1])[0]['weight']
            start_coor = [round(elem, 6) for elem in list(edge[0])]
            end_coor = [round(elem, 6) for elem in list(edge[1])]
            output.write(str(start_coor) + ';' + str(end_coor) + ';' + str(distance) + '\n')
    '''
        @input:     path of the shape file and the output for saving clean network
        @output:    Cleaned network

        This function read the input shape file and convert it into network for cleaning. After converting it simplify the
        graph by calling simplify_graph() and write the cleaned network in form of shapefiles
    '''

    def graph_convertor(self):
        G = self.shape_convertor()
        # print("Number of Nodes in the graph, ", len(G.nodes))
        # print("Number of Edges in the graph, ", len(G.edges))
        # simplify_graph = GraphSimplify(G)
        # new_G = simplify_graph.simplify_graph()

        # print("Number of Nodes after simplifying, ", len(new_G.nodes))
#         self.create_vertex_file(new_G)
#         self.create_edges_file(new_G)
        self.create_vertex_file(G)
        self.create_edges_file(G)
        
#         multiDi_to_simple = MultiDiToSimple(new_G)
        multiDi_to_simple = MultiDiToSimple(G)
        new_simple_graph = multiDi_to_simple.convert_MultiDi_to_Simple()
        
        pos = {k: v for k,v in enumerate(new_simple_graph.nodes())}
        # print(pos)
        self.positions = pos
        # print(pos) ## tu jest tak jak w arcgisie czyli ok
        
        self.create_edges_vertex_shape(new_simple_graph)

#         return new_G
        return G
