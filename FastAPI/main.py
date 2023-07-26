from fastapi import FastAPI, File, UploadFile
from starlette.middleware.cors import CORSMiddleware
from fastapi import Response, Query, Depends, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from database import SessionLocal, engine
import crud, models, schemas
from sqlalchemy.orm import Session

import json
import os
from io import BytesIO
import zipfile
import subprocess

import fiona
from shapely.geometry import shape
import geopandas as gpd
from PIL import Image

from shp2osm import shp2osm
from parse_georef import getGcpsFromPixels, transform_ogr, getGcpsFromWGS, save_to_postgres
from networkx_analysis import DrawGraph
from . import postprocessing


models.Base.metadata.create_all(bind=engine)

IMAGE_DIR = r''  # Image directory path
SCHEMA = ''  # Postgres Schema for database storing results from analysis
DBNAME = ''  # Name database in postgres

DBUSER = ''
DBPASSWORD = ''
PORT = ''
DBADDRESS = 'localhost'

USER = 'user'

app = FastAPI()
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

origins = '*'
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/getImages/")
def get_images():
    imgs = os.listdir(IMAGE_DIR)

    img_dict = {}
    for i, img in enumerate(imgs):
        if img.split('.')[-1] in ('PNG', 'png', 'jpg', 'tif'):
            img_dict[i] = img
    return img_dict

@app.get("/getNumGcps/{image}")
def get_ngcps(image: str, db: Session = Depends(get_db)):
    ngcps = crud.get_number_gcps(db, imagename=image)
    return ngcps


@app.get("/clearGCPs/{image}")
def clear_gcps(image: str, db: Session = Depends(get_db)):
    num_rows_deleted = db.query(models.Gcps).filter(models.Gcps.image_name==image).delete()
    db.commit()
    return num_rows_deleted

@app.get("/clear_vector/{image}")
def clear_vector(image: str, db: Session = Depends(get_db)):
    num_rows_deleted = db.query(models.VectorData).filter(models.VectorData.image_name==image).delete()
    db.commit()
    return num_rows_deleted

@app.get("/getGcps/{image}")
def get_gcps(image: str, db: Session = Depends(get_db)):
    db_gcps = crud.get_gcps_by_imagename(db, image)

    pixel_gcp = {"type": 'FeatureCollection', "features": []}
    wgs_gcp = {"type": 'FeatureCollection', "features": []}
    for gcp in db_gcps:
        pixel_gcp['features'].append({'type': 'Feature', 'properties': {'gcp_id': gcp.gcp_id, 'date': gcp.date, 'time': gcp.time},
         'geometry': {"type":"Point","coordinates":[gcp.pixel_x, gcp.pixel_y]}
        })

        wgs_gcp['features'].append({'type': 'Feature', 'properties': {'gcp_id': gcp.gcp_id, 'date': gcp.date, 'time': gcp.time},
         'geometry': {"type":"Point","coordinates":[gcp.wgs_lng, gcp.wgs_lat]}
        })
    return {'pixel_gcp': pixel_gcp, 'wgs_gcp': wgs_gcp}     

@app.get("/getLatestVector/{image}")
def get_latest_vector(image: str, db: Session = Depends(get_db)):
    latest_vector = crud.get_latest_vector(db, image)
    if latest_vector is None:
        return None
    json_object = json.loads(latest_vector[0])
    return JSONResponse(content=json_object)


@app.get("/getNumVector/{image}")
def get_nvector(image: str, db: Session = Depends(get_db)):
    nvector = crud.get_number_vector(db, imagename=image)
    return nvector


@app.get("/getNumResult/{image}")
def get_nresult(image: str, db: Session = Depends(get_db)):
    nresult = crud.get_number_result(db, imagename=image)
    return nresult


@app.get("/getLatestView/{image}")
def getLatestView(image: str, db: Session = Depends(get_db)):
    latest_view = crud.get_latest_view(db, image)
    if latest_view is None:
        return None
    return JSONResponse(content=latest_view[0])


@app.get("/getSpaceSyntaxView/{image}/{analysis_type}")
def getSpaceSyntaxView(image: str, analysis_type: str, db: Session = Depends(get_db)):
    latest_view = crud.get_latest_ss_view(db, image, analysis_type)
    if latest_view is None:
        return None
    return JSONResponse(content=latest_view[0])


class GeorefData(BaseModel):
    imagename: str
    pixel: dict
    wgs: dict
    date: str
    time:str

@app.post("/send_georef/")
async def send_georef(georef_data: GeorefData, db: Session = Depends(get_db) ):
    imagename = georef_data.imagename
    pixel_data = georef_data.pixel
    wgs_data = georef_data.wgs

    num_rows_deleted = db.query(models.Gcps).filter(models.Gcps.image_name==imagename).delete()
    db.commit()

    for p in pixel_data.keys():
        crud.create_gcp(db, imagename=imagename, gcpid=p, pixelcoords=pixel_data[p], wgscoords=wgs_data[p], date=georef_data.date, time=georef_data.time)
    return georef_data

@app.post("/send_map/")
async def send_map(file: UploadFile = File(...) ):
    contents = await file.read()
    img_validate = Image.open(BytesIO(contents))

    with open(fr"{IMAGE_DIR}/{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}

class VectorData(BaseModel):
    type: str
    features: list
    imagename: str

@app.post("/send_vector/")
async def send_vector(vector_data: VectorData, db: Session = Depends(get_db)):
    json_vector = VectorData.parse_obj(vector_data).json()
    crud.create_vector_data(db, imagename=vector_data.imagename, vector_json=json_vector)

    db_gcps = crud.get_gcps_by_imagename(db, vector_data.imagename)
    georef_annotation = {"body": 
                            {"features": []}
                        }
    for gcp in db_gcps:
        feature_json = {"id": gcp.gcp_id,
            "properties": {
                "pixelCoords": [gcp.pixel_x, gcp.pixel_y]
             },
            "geometry": {
                "type": "Point",
                "coordinates": [gcp.wgs_lng, gcp.wgs_lat]
            }
         }
        georef_annotation['body']['features'].append(feature_json)

    gcps_pixels = getGcpsFromPixels(georef_annotation)
    gcps_wgs = getGcpsFromWGS(georef_annotation)
    
    IMAGENAME = str(vector_data.imagename).split('.')[0]  # without extension
    with open(fr'vector/vector_{IMAGENAME}.json', 'w') as f:
        f.write(json_vector)

    OUT_FILE = fr'./Data/wgs_{IMAGENAME}.shp'
    transform_ogr(gcps_pixels, f.name, OUT_FILE, "ESRI Shapefile")

    # CNAME = 'olint'
    path_dest = (fr'./Data/{IMAGENAME}/NewShape/nodes.shp')
    path_dest2 = (fr'./Data/{IMAGENAME}/NewShape/edges.shp')
    path_dest3 = (fr'./Data/{IMAGENAME}/NewShape/ebc_{IMAGENAME}.shp')
    DrawGraph(path_dest, path_dest2, path_dest3, IMAGENAME)

    OUT_FILE = fr'{IMAGENAME}_bet.json'
    transform_ogr(gcps_wgs, path_dest3, OUT_FILE, "GeoJSON")

    with open(OUT_FILE, 'r') as out:
        data = out.read()
    obj = json.loads(data)
    return JSONResponse(content=obj)


@app.get("/perform_analysis/{imagename}")
async def perform_analysis(imagename: str, db: Session = Depends(get_db)):
    # GET vector_data FROM DB
    latest_vector = crud.get_latest_vector(db, imagename)
    json_vector = json.loads(latest_vector[0])  # get geojson_data for image

    db_gcps = crud.get_gcps_by_imagename(db, imagename)

    # Creating new geojson (dict)
    georef_annotation = {"body": 
                            {"features": []}
                        }
    for gcp in db_gcps:
        feature_json = {"id": gcp.gcp_id,
            "properties": {
                "pixelCoords": [gcp.pixel_x, gcp.pixel_y]
             },
            "geometry": {
                "type": "Point",
                "coordinates": [gcp.wgs_lng, gcp.wgs_lat]
            }
         }
        georef_annotation['body']['features'].append(feature_json)

    gcps_pixels = getGcpsFromPixels(georef_annotation)
    gcps_wgs = getGcpsFromWGS(georef_annotation)
    
    IMAGENAME = str(imagename).split('.')[0]  # without extension
    vector_fpath = f'vector/vector_{IMAGENAME}.shp'
    postprocessing.find_intersections(json_vector, vector_fpath)

    OUT_FILE = fr'./Data/wgs/wgs_{IMAGENAME}.shp'
    transform_ogr(gcps_pixels, vector_fpath, OUT_FILE, "ESRI Shapefile")
    
    gdf = gpd.read_file(OUT_FILE, crs='epsg:4326')
    utm_crs = gdf.estimate_utm_crs()
    gdf = gdf.to_crs(utm_crs)

    UTM_FILE = fr'./Data/utm/utm_{IMAGENAME}.shp'
    gdf.to_file(UTM_FILE)

    path_dest3 = (fr'./Data/{IMAGENAME}/NewShape/ebc_{IMAGENAME}.shp')
    res_json_4326 = json.loads(DrawGraph(UTM_FILE, path_dest3, IMAGENAME, imagename))

    # save geometry 4326 in db in geom field
    crud.delete_results_by_image(db, imagename=imagename)
    save_to_postgres(path_dest3, "networkx_results", IMAGENAME)
    
    OUT_FILE = fr'./networkx_results/{IMAGENAME}_bet.json'
    transform_ogr(gcps_wgs, path_dest3, OUT_FILE, "GeoJSON")

    with open(OUT_FILE, 'r') as out:
        data = out.read()
    res_json_pixel = json.loads(data)

    crud.delete_view_by_image(db, imagename=imagename)
    crud.create_view_data(db, imagename=imagename, geojson_4326=res_json_4326, geojson_pixel=res_json_pixel)
    return JSONResponse(content=res_json_pixel)


def perform_spacesyntax(imagename, pathIn, user):
    command = fr'docker run -v {pathIn}:/results space_syntax {imagename}.osm -u {user}'
    subprocess.run(command, shell=True)


@app.get("/perform_ss_analysis/{imagename}")
async def perform_ss_analysis(imagename: str, db: Session = Depends(get_db)):

    # GET vector_data FROM DB
    latest_vector = crud.get_latest_vector(db, imagename)
    json_vector = json.loads(latest_vector[0])  # get geojson_data for image
    
    db_gcps = crud.get_gcps_by_imagename(db, imagename)

    # Creating new geojson (dict)
    georef_annotation = {"body": 
                            {"features": []}                    }
    for gcp in db_gcps:
        feature_json = {"id": gcp.gcp_id,
            "properties": {
                "pixelCoords": [gcp.pixel_x, gcp.pixel_y]
             },
            "geometry": {
                "type": "Point",
                "coordinates": [gcp.wgs_lng, gcp.wgs_lat]
            }
         }
        georef_annotation['body']['features'].append(feature_json)

    gcps_pixels = getGcpsFromPixels(georef_annotation)
    gcps_wgs = getGcpsFromWGS(georef_annotation)
    
    IMAGENAME = str(imagename).split('.')[0]  # without extension
    vector_fpath = f'vector/vector_{IMAGENAME}.shp'
    postprocessing.find_intersections(json_vector, vector_fpath)

    OUT_FILE = fr'./Data/wgs/wgs_{IMAGENAME}.shp'
    transform_ogr(gcps_pixels, vector_fpath, OUT_FILE, "ESRI Shapefile")  # Create shapefile - vector in WGS (OUT_FILE)
    
    gdf = gpd.read_file(OUT_FILE, crs='epsg:4326')
    utm_crs = gdf.estimate_utm_crs()

    # # convert OUT_FILE to osm
    shp2osm(OUT_FILE, fr'./spacesyntax_results/{IMAGENAME}.osm')
    perform_spacesyntax(IMAGENAME, fr'./spacesyntax_results/', USER)
    crud.delete_axial_by_image(db, imagename=imagename)
    crud.delete_segment_by_image(db, imagename=imagename)
    save_to_postgres(fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}/osm.axial.shp', "axial_results", imagename, 'axial', str(utm_crs))
    save_to_postgres(fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}/osm.segment.shp', "segment_results", imagename, 'segment', str(utm_crs))
    
    UTM_FILE_AXIAL = fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_axial.shp'
    UTM_FILE_SEGMENT = fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_segment.shp'

    gdf_axial = gpd.read_file(UTM_FILE_AXIAL)
    gdf_axial = gdf_axial.set_crs(utm_crs, allow_override=True)

    gdf_segment = gpd.read_file(UTM_FILE_SEGMENT)
    gdf_segment = gdf_segment.set_crs(utm_crs, allow_override=True)

    gdf_axial = gdf_axial.to_crs(4326)
    gdf_segment = gdf_segment.to_crs(4326)

    gdf_axial.to_file(UTM_FILE_AXIAL)
    gdf_segment.to_file(UTM_FILE_SEGMENT)
    
    OUT_FILE_AXIAL = fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_axial.json'
    transform_ogr(gcps_wgs, fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_axial.shp', OUT_FILE_AXIAL, "GeoJSON")
    with open(fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}/osm.axial.geojson', 'r') as f:
        axial_json_4326 = json.loads(f.read())

    with open(OUT_FILE_AXIAL, 'r') as out:
        data = out.read()
    axial_json_pixel = json.loads(data)

    OUT_FILE_SEGMENT = fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_segment.json'
    transform_ogr(gcps_wgs, fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}_segment.shp', OUT_FILE_SEGMENT, "GeoJSON")
    with open(fr'./spacesyntax_results/{IMAGENAME}/{IMAGENAME}/osm.segment.geojson', 'r') as f:
        segment_json_4326 = json.loads(f.read())

    with open(OUT_FILE_SEGMENT, 'r') as out:
        data = out.read()
    segment_json_pixel = json.loads(data)

    crud.delete_ss_view_by_image(db, imagename=imagename)
    crud.create_ss_view(db, imagename=imagename, geojson_4326=axial_json_4326, geojson_pixel=axial_json_pixel, analysis_type='axial')
    crud.create_ss_view(db, imagename=imagename, geojson_4326=segment_json_4326, geojson_pixel=segment_json_pixel, analysis_type='segment')
    return None


@app.post("/create_vector/")
async def create_vector(vector_data: VectorData, db: Session = Depends(get_db)):
    json_vector = VectorData.parse_obj(vector_data).json()
    crud.create_vector_data(db, imagename=vector_data.imagename, vector_json=json_vector)
    obj = json.loads(json_vector)
    return JSONResponse(content=obj)


@app.post("/update_vector/")
async def update_vector(vector_data: VectorData, db: Session = Depends(get_db)):
    json_vector = VectorData.parse_obj(vector_data).json()
    crud.update_vector_data(db, imagename=vector_data.imagename, vector_json=json_vector)   
    obj = json.loads(json_vector)

    return JSONResponse(content=obj)

def zipfiles(filenames, imagename):
    zip_filename = f"a{imagename}.zip"
    s = BytesIO()
    zf = zipfile.ZipFile(s, "w")
    for fpath in filenames:
        fdir, fname = os.path.split(fpath)
        zf.write(fpath, fname)
    zf.close()
    resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={'Content-Disposition': f'attachment;filename={zip_filename}'})
    return resp

@app.get("/download_shp/{image}/{atype}")
async def download_shp(image: str, atype: str):
    
    imagename = image.split('.')[0]
    dirpath = fr'./export/{imagename}/{atype}'
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    dbname = DBNAME
    schema = SCHEMA
    if atype == "networkx":
        table  = "networkx_results"
        command = fr"""pgsql2shp -f "{dirpath}/networkx_{imagename}.shp" -h {DBADDRESS} -u {DBUSER} -P {DBPASSWORD} -p {PORT} {DBNAME}  "select * from {SCHEMA}.{table} where image_name = '{image}';"
        """
        subprocess.run(command, shell=True)

    elif atype == "spacesyntax":
        command = fr"""pgsql2shp -f "{dirpath}/axial_{imagename}.shp" -h {DBADDRESS} -u {DBUSER} -P {DBPASSWORD} -p {PORT} {DBNAME}  "select * from {SCHEMA}.axial_results where image_name = '{image}';"
        """
        subprocess.run(command, shell=True)
        command = fr"""pgsql2shp -f "{dirpath}/segment_{imagename}.shp" -h {DBADDRESS} -u {DBUSER} -P {DBPASSWORD} -p {PORT} {DBNAME}  "select * from {SCHEMA}.segment_results where image_name = '{image}';"
        """
        subprocess.run(command, shell=True)

    shps = []
    for filename in os.listdir(dirpath):
        shps.append(os.path.join(dirpath, filename))
    return zipfiles(shps, f'{atype}_{imagename}')

