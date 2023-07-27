
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


## Architecture
![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/architecture-diagram.png)


## Deployment
To deploy application, you need to install and setup a few components.

Firstly, install python dependencies from API directory:
```
pip install -r requirements.txt
```
Pobranie leafleta, pluginów do leaflate (geoman, leaflet-iiif), wrzucenie ich do static/

###  IIIF server - Cantaloupe - 5.05
uruchomić serwer, wskazać ścieżkę do folderu ze zdjęciami (cantaloupe.properties) i podać ją w main.py
zdefiniowanie ścieżky w main.py - Image_DIR


### Database
for storing digitized, georeferenced data (input data from user) and for storing results of network analysis

pobranie postgresa, instalacja, zapamiętać passy 
https://www.postgresql.org/download/

Zainstalować rozszerzenie PostGIS (np. poprzez StackBuilder). 
Stworzyć  bazę danych(możesz używać pg admin - aplikację gui). 

W pliku db_params.py ustawić parametry bazy.

dodać do PATH bin postgisa (żeby mieć ogr2ogr, pg.)


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
