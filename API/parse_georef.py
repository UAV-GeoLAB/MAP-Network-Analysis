import json
import re
import os
import subprocess
from db_params import SCHEMA, DBNAME, DBUSER, DBPASSWORD, PORT, DBADDRESS

def getImageDimension(ann):
	selector = ann['target']['selector']['value']
	selectorReg = r"^<svg\swidth=\"(\d+)\"\sheight=\"(\d+)\"><polygon points=\"(.+)\""
	selectorResult = re.search(selectorReg, selector).groups()
	width = selectorResult[0]
	height = selectorResult[1]
	points = selectorResult[2].split(" ")
	return width, height, points

def getGcpsFromPixels(ann):
	gcps_commands = []
	features = ann['body']['features']
	image_points = []
	world_points = []
	for f in features:
		image_points.append(f['properties']['pixelCoords'])
		world_points.append(f['geometry']['coordinates'])
		gcps_commands.append(' -gcp ')
		gcps_commands.append(f"{f['properties']['pixelCoords'][0]} {f['properties']['pixelCoords'][1]} {f['geometry']['coordinates'][0]} {f['geometry']['coordinates'][1]} ")
	return gcps_commands

def getGcpsFromWGS(ann):
	gcps_commands = []
	features = ann['body']['features']
	image_points = []
	world_points = []
	for f in features:
		image_points.append(f['properties']['pixelCoords'])
		world_points.append(f['geometry']['coordinates'])

		gcps_commands.append(' -gcp ')
		gcps_commands.append(f"{f['geometry']['coordinates'][0]} {f['geometry']['coordinates'][1]} {f['properties']['pixelCoords'][0]} {f['properties']['pixelCoords'][1]} ")

	return gcps_commands


def transform_ogr(gcp_commands, in_filepath, out_filepath, out_format):
	command = fr'ogr2ogr -f "{out_format}" -a_srs EPSG:4326 -order 1'

	for gcp in gcp_commands:
		command += gcp

	out_file = os.path.abspath(out_filepath)
	in_file = os.path.abspath(in_filepath)

	command += fr'{out_file} {in_file}'
	subprocess.run(command, shell=True)


def transform_to_wgs(gcp_commands, in_filepath, out_filepath, out_format):
	command = fr'ogr2ogr -f "{out_format}" -t_srs EPSG:4326'
	for gcp in gcp_commands:
		command += gcp

	out_file = os.path.abspath(out_filepath)
	in_file = os.path.abspath(in_filepath)

	command += fr'{out_file} {in_file}'
	subprocess.run(command, shell=True)


def save_to_postgres(source_path, dest_table, imagename_with_ext, s = '', crs='EPSG:4326'):
	imagename = imagename_with_ext.split('.')[0]
	if s == '':
		command = f'ogr2ogr -f "PostgreSQL" -append PG:"dbname={DBNAME} user={DBUSER} password={DBPASSWORD}" "{source_path}" -nln {dest_table} -s_srs "{crs}" -t_srs "EPSG:4326" -geomfield geom_4326'
	else:
		source_dir = fr'./spacesyntax_results/{imagename}'
		new_source = os.path.join(source_dir, f"{imagename}_{s}.shp")
		command = f'ogr2ogr -f "ESRI Shapefile" -a_srs "{crs}" {new_source} {source_path}'  # change filename of shp 
		subprocess.run(command, shell=True)										 # (because inital filename is with dot what causes problems with ogr)
		command = fr'''ogr2ogr -f "PostgreSQL" -append PG:"dbname={DBNAME} user={DBUSER} password={DBPASSWORD}" "{new_source}" -nln {dest_table} -s_srs "{crs}" -t_srs "EPSG:4326" -geomfield geom_4326 -sql "SELECT *,'{imagename_with_ext}' as image_name FROM \"{imagename}_{s}\""'''

	subprocess.run(command, shell=True)
