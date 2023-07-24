import logging
import ogr2osm


def shp2osm(in_path, out_path):
	
	# 1. Set the logging level of the logger object named 'ogr2osm' to the desired output level

	ogr2osmlogger = logging.getLogger('ogr2osm')
	ogr2osmlogger.setLevel(logging.ERROR)
	ogr2osmlogger.addHandler(logging.StreamHandler())

	# 2. Required parameters for this example:

	# - datasource_parameter is a variable holding the input filename, or a
	#   database connection such as "PG:dbname=pdx_bldgs user=emma host=localhost"
	datasource_parameter = in_path

	# - in case your datasource is a database, you will need a query
	# query = ...

	# - the output file to write
	output_file = out_path

	# 3. Create the translation object. If no translation is required you
	#    can use the base class from ogr2osm, otherwise you need to instantiate
	#    a subclass of ogr2osm.TranslationBase
	translation_object = ogr2osm.TranslationBase()

	# 4. Create the ogr datasource. You can specify a source projection but
	#    EPSG:4326 will be assumed if none is given and if the projection of the
	#    datasource is unknown.
	datasource = ogr2osm.OgrDatasource(translation_object)
	# Optional constructor parameters:
	# - source_proj4: --proj4 parameter
	# - source_epsg: --epsg parameter
	# - gisorder: --gis-order parameter
	# - source_encoding: --encoding parameter
	datasource.open_datasource(datasource_parameter)
	# Optional open_datasource parameters:
	# - prefer_mem_copy: --no-memory-copy parameter

	# 5. If the datasource is a database then you must set the query to use.
	#    Setting the query for any other datasource is useless but not an error.
	# datasource.set_query(query)

	# 6. Instantiate the ogr to osm converter class ogr2osm.OsmData and start the
	#    conversion process
	osmdata = ogr2osm.OsmData(translation_object)
	# Optional constructor parameters:
	# - rounding_digits: --rounding-digits parameter
	# - max_points_in_way: --split-ways parameter
	# - add_bounds: --add-bounds parameter
	# - start_id: --id parameter
	osmdata.process(datasource)

	# 7. Instantiate either ogr2osm.OsmDataWriter or ogr2osm.PbfDataWriter and
	#    invoke output() to write the output file. If required you can write a
	#    custom datawriter class by subclassing ogr2osm.DataWriterBase.
	datawriter = ogr2osm.OsmDataWriter(output_file)
	# Optional constructor parameters:
	# - never_upload: --never-upload parameter
	# - no_upload_false: --no-upload-false parameter
	# - never_download: --never-download parameter
	# - locked: --locked parameter
	# - significant_digits: --significant-digits parameter
	# - suppress_empty_tags: --suppress-empty-tags parameter
	osmdata.output(datawriter)