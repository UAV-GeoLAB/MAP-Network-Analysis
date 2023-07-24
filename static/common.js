function getProperZoom(width, height, map_object) {
   var zoom = 0; 
   console.log(width, height, map_object)
    for (var i=0; i < 10; i++) {
        zoom += 1;
        maxPoint = map_object.unproject([width,height], zoom);

        console.log(maxPoint)
        if (maxPoint.lng < 540 && maxPoint.lat > -540)
            break;
    }

    // Draw bounding box in order to check if zoom is calculated correctly
    var northWest = map_object.unproject([0,0], zoom);
	var northEast = map_object.unproject([width,0], zoom);
    var southWest = map_object.unproject([0,height], zoom); 
    var southEast = map_object.unproject([width,height], zoom);

    var bounding_box = new L.Polyline([northWest, northEast, southEast, southWest, northWest], {
    	color: "orange",
    	fillOpacity:0
    }).addTo(map_object);

    return zoom;
}


