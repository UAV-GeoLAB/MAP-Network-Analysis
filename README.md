
# Graph Analysis On Street Network In A Web Browser

The tool is a prototype system for comparing spatial layouts in ancient cities. It allows to conduct simple GIS operations in a web browser (digitizing and georeferencing data) and then perform network analysis on input data. 

## Dependencies:
- Leaflet (https://leafletjs.com/)
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


## Deployment
To deploy application, you need to install and setup a few components.

Firstly, install python dependencies from API directory:
```
pip install -r requirements.txt
```
Pobranie leafleta, pluginów do leaflate (geoman, leaflet-iiif), wrzucenie ich do static/

###  IIIF image server - Cantaloupe
Download Cantaloupe v5.0.5 from https://github.com/cantaloupe-project/cantaloupe/releases.
Specify directory path for storing images in cantaloupe.properties and run server (according to instruction provided in the link above).
Specify above path as well in *API/main.py* as the value of variable:
```
IMAGE_DIR = r'\path\to\images'  # Image directory path served by IIIF server

```

### Database
for storing digitized, georeferenced data (input data from user) and for storing results of network analysis

Download PostgreSQL from https://www.postgresql.org/download/. Remember the password specified during installation!
Please download also PostGIS extension for PostgreSQL - you can do it from StackBuilder application

After installation, create database which will store digitized, georeferenced street networks and results of network analysis. You can do it using Postgres GUI application – pgAdmin.

After setup database, please specify database parameters in *API/db_params.py*.
Finally, add path of Postgres *bin* directory (with Postgis files) to environment variable PATH. In this *bin* folder there will be GDAL/OGR dependencies necessary in our system.


### API
Install FastAPI and uvicorn server.


# DOcker do space syntaxa

zainstalować dockera do spac syntaxa
container o nazwie space_syntax

w folderze gdzie jest DOckerfile
docker build --tag space_syntax .

### Adres API, ścieżki do plików html
Poniższa konfiguracja lokalnie, ale można zmienić wystawiając później na świat

W pliku urls.js definiuje się:
API_URL = 
IIIF_URL



## Funding
This work was supported by the National Science Centre (NCN), Poland as a part of MA-P Maloutena and Agora in the layout of Paphos: Modelling the cityscape of the Hellenistic and Roman capital of Cyprus project, OPUS 18 grant No. 2019/35/B/HS3/02296.
