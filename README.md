
# Graph Analysis On Street Network In A Web Browser

The tool is a prototype system for comparing spatial layouts in ancient cities. It allows to conduct simple GIS operations in a web browser (digitizing and georeferencing data) and then perform network analysis on input data. 

## Dependencies:
- Leaflet (https://leafletjs.com/)
- Leaflet plugins:
    - Leaflet-IIIF (https://github.com/mejackreed/Leaflet-IIIF)
    - Leaflet-Geoman (https://github.com/geoman-io/leaflet-geoman)
- PostgreSQL (https://www.postgresql.org.pl/) - relational database
- FastAPI (https://fastapi.tiangolo.com/) - API which allows to communicate between application and PostgreSQL database
- GDAL/OGR (https://live.osgeo.org/en/overview/gdal_overview.html)
- DepthMapX SpaceSyntax Docker (https://github.com/digitalcityscience/space-syntax)
- NetworkX python library (https://networkx.org/)
- Python 3.7+
- Other python libraries for processing spatial data



## Architecture
![alt text](https://github.com/UAV-GeoLAB/MAP-Network-Analysis/blob/main/references/architecture-diagram.png)


## Deployment
To deploy application, you need to install and setup a few components.

Firstly, install python dependencies from API directory:
```
pip install -r requirements.txt
```


### API
Install FastAPI and uvicorn server.



### Database
for storing digitized, georeferenced data (input data from user) and for storing results of network analysis




## Funding
This work was supported by the National Science Centre (NCN), Poland as a part of MA-P Maloutena and Agora in the layout of Paphos: Modelling the cityscape of the Hellenistic and Roman capital of Cyprus project, OPUS 18 grant No. 2019/35/B/HS3/02296.
