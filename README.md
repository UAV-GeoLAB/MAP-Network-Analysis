
# Graph Analysis On Street Network In A Web Browser

The tool is a prototype system for comparing spatial layouts in ancient cities. It allows to conduct simple GIS operations in a web browser (digitizing and georeferencing data) and then perform network analysis (networkx and spacesyntax analyses) on input data. 

Example screenshots from application
(The source of the base map: **Hoepfner and Schwandner, 1994**).
Digitization of street network:

![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/digitization-streetnetwork.png)

Georeferencing:

![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/georefernce.png)

Showing results of network analysis:

![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/results-spacesyntax.png)

## Dependencies:
- Leaflet 1.8.0(https://leafletjs.com/) – used in our system as the image viewer.
- Leaflet plugins:
    - Leaflet-IIIF (https://github.com/mejackreed/Leaflet-IIIF) – plugin which allows to handle IIIF resources in Leaflet.
    - Leaflet-Geoman (https://github.com/geoman-io/leaflet-geoman) – plugin which provides provide data vectorization functionality.
- PostgreSQL (https://www.postgresql.org.pl/) – relational database used to store geospatial data assigned to images (e.g., vectorized street network, georeferencing data),
- Python 3.7+ and libraries (see *API/requirements.txt*),
- FastAPI (https://fastapi.tiangolo.com/) - Python web framework to communicate our web application with database.
- GDAL/OGR (https://live.osgeo.org/en/overview/gdal_overview.html) – library used for georeferencing vector data.
- DepthMapX SpaceSyntax Docker (https://github.com/digitalcityscience/space-syntax)
- Cantaloupe (https://cantaloupe-project.github.io/) – image server which serces raster data for various zoom levels in accordance with the IIIF standard.


## Architecture
![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/architecture-diagram.png)
**Description of components**:
- Server side
    - Image API – IIIF API/image server responsible for sharing images and interactively displaying raster images with deep zoom,
    - Database – stores digitized, georeferenced data (input data from user) and  results of network analysis,
    - API – allows communication with database and docker container for Space Syntax analysis.
- Client side (Web Browser) consists of three main components
    - Digitalization of street network,
    - Georeferencing (acquisition of Ground Control Points),
    - Displaying results of network analyses with possiblity to download them in GIS format (Shapefile).

## Deployment
To deploy application, you need to install and setup a few components.
Steps below are describing way of deployment the system on **localhost**.


####  IIIF image server - Cantaloupe
Download Cantaloupe v5.0.5 from https://github.com/cantaloupe-project/cantaloupe/releases.
Specify directory path for storing images in cantaloupe.properties and run server (according to instruction provided in the link above).
Specify above path as well in *API/main.py* as the value of variable:
```
IMAGE_DIR = r'\path\to\images'  # Image directory path served by IIIF server
```

#### Database – PostgreSQL

Download PostgreSQL from https://www.postgresql.org/download/. Remember the password specified during installation!
Please download also PostGIS extension for PostgreSQL - you can do it from StackBuilder application

After installation, create database which will store digitized, georeferenced street networks and results of network analysis. You can do it using Postgres GUI application – pgAdmin.

After you setup database, **please specify database parameters** in *API/db_params.py*.
Finally, **add path of Postgres *bin* directory (with Postgis files) to environment variable PATH**. In this *bin* folder there will be GDAL/OGR dependencies necessary in our application.


#### API – Python and FastAPI
You need Python 3.7+. Change directory to *API* and install all Python libraries (dependencies) at right versions using:
```
pip install -r requirements.txt
```
Then run API server using:
```
uvicorn main:app
```

#### SpaceSyntax Docker
Download docker files from:
https://github.com/UAV-GeoLAB/space-syntax-for-MAP-project/tree/0a9e7a1243f05844e4a86a3c41df6ad67ad0eef2. 
It is docker from https://github.com/digitalcityscience/space-syntax, adopted for our application. 

After downloading docker files and changing to its root folder, build the SpaceSyntax Docker container with tag *space_syntax*:
```
docker build --tag space_syntax .
```

#### HTML and Javascript code
Please download source code of Leaflet and its plugins:
- https://github.com/Leaflet/Leaflet/releases/tag/v1.8.0
- https://github.com/mejackreed/Leaflet-IIIF
- https://github.com/geoman-io/leaflet-geoman.

Extract above files in *static* directory.

#### Further configuration
In *static/urls.js* you can change adresses of FastAPI and Cantaloupe server (if you want use these services on non-localhost adresses). You can also change paths for html files:
```
// Urls for static files (needed during deploymend)
var API_URL = "http://127.0.0.1:8000/" // localhost
var IIIF_URL = "http://127.0.0.1:8182/iiif/3/" // localhost
var EDITOR_URL = "./editor.html"
var VIEWER_URL = "./viewer.html"
var VIEWER_SS_URL = "./viewer_spacesyntax.html"
var GEOREFERENCE_URL = "./georeference.html"
```

## Funding
This work was supported by the National Science Centre (NCN), Poland as a part of MA-P Maloutena and Agora in the layout of Paphos: Modelling the cityscape of the Hellenistic and Roman capital of Cyprus project, OPUS 18 grant No. 2019/35/B/HS3/02296.
