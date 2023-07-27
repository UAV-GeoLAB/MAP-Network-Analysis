
# Graph Analysis On Street Network In A Web Browser

The tool is a prototype system for comparing spatial layouts in ancient cities. It allows to conduct simple GIS operations in a web browser (digitizing and georeferencing data) and then perform network analysis on input data. 

## Dependencies:
- Leaflet 1.8.0(https://leafletjs.com/)
- Leaflet plugins:
    - Leaflet-IIIF (https://github.com/mejackreed/Leaflet-IIIF)
    - Leaflet-Geoman (https://github.com/geoman-io/leaflet-geoman)
- PostgreSQL (https://www.postgresql.org.pl/)
- Python 3.7+ and libraries (see API/requirements.txt)
- GDAL/OGR (https://live.osgeo.org/en/overview/gdal_overview.html)
- DepthMapX SpaceSyntax Docker (https://github.com/digitalcityscience/space-syntax)
- Cantaloupe (https://cantaloupe-project.github.io/)


## Architecture
![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/architecture-diagram.png)
for storing digitized, georeferenced data (input data from user) and for storing results of network analysis

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

After you setup database, please specify database parameters in *API/db_params.py*.
Finally, add path of Postgres *bin* directory (with Postgis files) to environment variable PATH. In this *bin* folder there will be GDAL/OGR dependencies necessary in our application.


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
Download docker files from https://github.com/UAV-GeoLAB/space-syntax-for-MAP-project/tree/0a9e7a1243f05844e4a86a3c41df6ad67ad0eef2. It is docker from https://github.com/digitalcityscience/space-syntax, adopted for our application. 

After downloading docker files and changing to its root folder, build the SpaceSyntax Docker container with tag *space_syntax*:
```
docker build --tag space_syntax .
```

#### HTML and Javascript code
Please download source code of Leaflet and its plugins:
- https://github.com/Leaflet/Leaflet/releases/tag/v1.8.0
- https://github.com/mejackreed/Leaflet-IIIF
- https://github.com/geoman-io/leaflet-geoman.
Extract above file in *static* directory.

#### Further configuration
In *static/urls.js* you can change adresses of FastAPI and Cantaloupe server (if you want deploy these services on non-default adresses). You can also change paths for html files:
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
