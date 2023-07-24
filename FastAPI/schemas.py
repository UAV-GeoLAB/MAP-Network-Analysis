from typing import List, Union, Dict

from pydantic import BaseModel


class GcpsBase(BaseModel):
	image_name: str
	symbol_name: str
	

class Gcps(GcpsBase):
	pixel_x: float
	pixel_y: float
	wgs_lat: float
	wgs_lng: float

	class Config:
		orm_mode = True




