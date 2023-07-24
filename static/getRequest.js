function makeRequest(method, url) {
    return new Promise(function (resolve, reject) {
        let req = new XMLHttpRequest();
        req.open(method, url);
        req.onload = function() {
            if (this.status >= 200 && this.status < 300) {
                resolve(req.response);
            } else {
                reject ({
                    status: this.status,
                    statusText: req.statusText
                });
            }
        };

        req.onerror = function() {
            reject({
                status: this.status,
                statusText: req.statusText
            });
        };
        req.send();

    });
}

function makeRequestBlob(method, url) {
    return new Promise(function (resolve, reject) {
        let req = new XMLHttpRequest();
        req.responseType = 'blob';
        req.open(method, url);
        req.onload = function() {
            if (this.status >= 200 && this.status < 300) {
                resolve(req.response);
            } else {
                reject ({
                    status: this.status,
                    statusText: req.statusText
                });
            }
        };

        req.onerror = function() {
            reject({
                status: this.status,
                statusText: req.statusText
            });
        };
        req.send();

    });
}


function getRequest(url, map_obj) {
	var req = new XMLHttpRequest();
	req.responseType = 'json';
	req.open('GET', url);
	req.send(null);

    var ZOOM = null;

	req.onload = function() {
		var info = req.response;

		var w = info.width;
        var h = info.height;

       
       var zoom = 0; 
        for (var i=0; i < 10; i++) {
            zoom += 1;
            maxPoint = map_obj.unproject([w,h], zoom);
			console.log(maxPoint);


            if (maxPoint.lng < 500 && maxPoint.lat > -500)
                break;
        }
        PROPER_ZOOM = zoom;

        var northEast = map_obj.unproject([w,0], zoom);
        var southWest = map_obj.unproject([0,h], zoom); 
        var northWest = map_obj.unproject([0,0], zoom);
        var southEast = map_obj.unproject([w,h], zoom);
        
        var bounding_box = new L.Polygon([northWest, northEast, southEast, southWest], {
        	color: "orange",
        	fillOpacity:0
        }).addTo(map_obj);      
	}
}


function getFeaturesInPixels(map_object, zoom) {
    var drawnFeaturesInPixels = L.featureGroup();
   
   // convert input features to pixel coordinates
    inputFeatures.eachLayer(function(layer){
        for (var i=0; i < layer._latlngs.length;i++) {
            pixel_crs = map_object.project([layer._latlngs[i]['lat'], layer._latlngs[i]['lng']], zoom);    
        }
        drawnFeaturesInPixels.addLayer(layer);
     });

    var drawnGeojson = drawnFeaturesInPixels.toGeoJSON(); // convert to GeoJSON
    for (var i=0; i<drawnGeojson.features.length; i++) {
        for (var j=0; j<drawnGeojson.features[i].geometry.coordinates.length; j++) {
            var longlat = drawnGeojson.features[i].geometry.coordinates[j];
            pixel_crs = map_object.project([longlat[1], longlat[0]], zoom); // exchange position for latitude i longitude
            drawnGeojson.features[i].geometry.coordinates[j] = [pixel_crs['x'], pixel_crs['y']];
        }
    }

    return drawnGeojson           
};


function saveVector(geojsonObject, imagename, map_object, zoom) {
    geojsonObject['imagename'] = imagename;
    console.log(geojsonObject);

    let xhr = new XMLHttpRequest();
    if (Object.keys(inputFeatures._layers).length > 1) // if vector data exists, then update  
        xhr.open("POST", `${API_URL}update_vector/`);
    else // vector data are created
        xhr.open("POST", `${API_URL}create_vector/`);
    
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.send(JSON.stringify(geojsonObject));

    xhr.onload = function() {

        // Clean input Features to fill it with new features
        inputFeatures.eachLayer(function(layer){
            inputFeatures.removeLayer(layer);
            layer.remove();
             
        });

        var geojson_res = JSON.parse(xhr.responseText);
        var geojson_layer = L.geoJson(geojson_res, {
            coordsToLatLng: function (coords) {
                new_coords = map_object.unproject([coords[0],coords[1]], zoom);
                return new L.LatLng(new_coords.lat, new_coords.lng);
        },
            style: {
                color: 'green'
            },
        }).addTo(map_object)

        geojson_layer.eachLayer(function (layer) {
          inputFeatures.addLayer(layer);
        });
        myFunction();
        inputFeatures.eachLayer(function(layer){
            layer.on('pm:edit', (e) => {
              console.log(e);
              geojson_to_save = getFeaturesInPixels(map_object, zoom);
              saveVector(geojson_to_save, imagename, map_object, zoom);
            });
        });
    }
};