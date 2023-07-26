from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


from database import Base



class Gcps(Base):
	__tablename__ = "gcps"

	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	gcp_id = Column(String)
	pixel_x = Column(Float)
	pixel_y = Column(Float)
	wgs_lat = Column(Float)
	wgs_lng = Column(Float)
	date = Column(String)
	time = Column(String)



class VectorData(Base):
	__tablename__ = "vector_data"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	geojson_data = Column(JSON)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	last_modified = Column(DateTime(timezone=True), onupdate=func.now())



class ResultsData(Base):
	__tablename__ = "networkx_results"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	last_modified = Column(DateTime(timezone=True), onupdate=func.now())


class ViewData(Base):
	__tablename__ = "view_data"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	geojson_data_4326 = Column(JSON)
	geojson_data_pixel = Column(JSON)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	last_modified = Column(DateTime(timezone=True), onupdate=func.now())


class AxialResults(Base):
	__tablename__ = "axial_results"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	

class SegmentResults(Base):
	__tablename__ = "segment_results"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	
class SpaceSyntaxView(Base):
	__tablename__ = "spacesyntax_view"
	id = Column(Integer, primary_key=True)
	image_name = Column(String)
	geojson_data_4326 = Column(JSON)
	geojson_data_pixel = Column(JSON)
	created_at = Column(DateTime(timezone=True), server_default=func.now())
	last_modified = Column(DateTime(timezone=True), onupdate=func.now())
	analysis_type = Column(String)