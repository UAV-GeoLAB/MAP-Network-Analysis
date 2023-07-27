from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from sqlalchemy import func
import models, schemas
import uuid


def create_gcp(db: Session, imagename: str, gcpid: str, pixelcoords: list, wgscoords: list, date:str, time:str):
	db_gcp = models.Gcps(image_name=imagename, gcp_id=gcpid, pixel_x=pixelcoords[0], pixel_y=pixelcoords[1], wgs_lat=wgscoords[0], wgs_lng=wgscoords[1], date=date, time=time)
	db.add(db_gcp)
	db.commit()
	db.refresh(db_gcp)
	return db_gcp


def create_vector_data(db: Session, imagename: str, vector_json: str):
	db_vector = models.VectorData(image_name=imagename, geojson_data=vector_json)
	db.add(db_vector)
	db.commit()
	db.refresh(db_vector)
	return db_vector

def update_vector_data(db: Session, imagename: str, vector_json: str):
	query = db.query(models.VectorData).filter(models.VectorData.image_name==imagename).update({'geojson_data': vector_json})
	db.commit()
	return query


def create_view_data(db: Session, imagename: str, geojson_4326: str, geojson_pixel: str):
	db_viewdata = models.ViewData(image_name=imagename, geojson_data_4326=geojson_4326, geojson_data_pixel=geojson_pixel)
	db.add(db_viewdata)
	db.commit()
	db.refresh(db_viewdata)
	return db_viewdata


def create_ss_view(db: Session, imagename: str, geojson_4326: str, geojson_pixel: str, analysis_type: str):
	db_viewdata = models.SpaceSyntaxView(image_name=imagename, geojson_data_4326=geojson_4326, geojson_data_pixel=geojson_pixel, analysis_type=analysis_type)
	db.add(db_viewdata)
	db.commit()
	db.refresh(db_viewdata)
	return db_viewdata


def get_gcps_by_imagename(db: Session, imagename: str):
	return db.query(models.Gcps).filter(models.Gcps.image_name==imagename).all()

def get_number_gcps(db: Session, imagename: str):
	return db.query(models.Gcps).filter(models.Gcps.image_name==imagename).count()

def get_number_vector(db: Session, imagename: str):
	return db.query(models.VectorData).filter(models.VectorData.image_name==imagename).count()

def get_number_result(db: Session, imagename: str):
	return db.query(models.ResultsData).filter(models.ResultsData.image_name==imagename).count()

def get_latest_vector(db:Session, imagename:str):
	query = text(f'''
		SELECT geojson_data, created_at
		FROM vector_data
		WHERE image_name = '{imagename}'
		ORDER BY created_at DESC
	''')

	return db.execute(query).first()

def get_latest_view(db:Session, imagename:str):
	query = text(f'''
		SELECT geojson_data_pixel, created_at
		FROM view_data
		WHERE image_name = '{imagename}'
		ORDER BY created_at DESC
	''')

	return db.execute(query).first()

def get_latest_ss_view(db:Session, imagename:str, analysis_type: str):
	query = text(f'''
		SELECT geojson_data_pixel, created_at
		FROM spacesyntax_view
		WHERE image_name = '{imagename}' AND analysis_type='{analysis_type}'
		ORDER BY created_at DESC
	''')

	return db.execute(query).first()
def delete_results_by_image(db: Session, imagename: str):
	num_deleted = db.query(models.ResultsData).filter(models.ResultsData.image_name==imagename).delete()
	db.commit()
	return num_deleted

def delete_axial_by_image(db: Session, imagename: str):
	try:
		num_deleted = db.query(models.AxialResults).filter(models.AxialResults.image_name==imagename).delete()
		db.commit()
		return num_deleted
	except:
		return None
	

def delete_segment_by_image(db: Session, imagename: str):
	try:
		num_deleted = db.query(models.SegmentResults).filter(models.SegmentResults.image_name==imagename).delete()
		db.commit()
		return num_deleted
	except:
		return None

def delete_view_by_image(db: Session, imagename: str):
	num_deleted = db.query(models.ViewData).filter(models.ViewData.image_name==imagename).delete()
	db.commit()
	return num_deleted

def delete_ss_view_by_image(db: Session, imagename: str):
	num_deleted = db.query(models.SpaceSyntaxView).filter(models.SpaceSyntaxView.image_name==imagename).delete()
	db.commit()
	return num_deleted

def add_geometry_columns(db: Session):
	query = text(f'''
		ALTER TABLE networkx_results
	  ADD COLUMN IF NOT EXISTS geom_4326 geometry(LINESTRING, 4326);
		ALTER TABLE axial_results
	  ADD COLUMN IF NOT EXISTS geom_4326 geometry(LINESTRING, 4326);
		ALTER TABLE segment_results
	  ADD COLUMN IF NOT EXISTS geom_4326 geometry(LINESTRING, 4326);

	''')
	print(db.execute(query))
	return db.commit()


def add_postgis_extension(db:Session):
	query = text(f'''
		CREATE EXTENSION IF NOT EXISTS postgis;

	''')
	print(db.execute(query))
	return db.commit()