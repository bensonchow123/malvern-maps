var imageUrl = '/static/images/map.png';
var imageBounds= [[0, 0], [1567, 1653]];

var map = L.map('map', {
    maxZoom: 5,
    minZoom: -1.5,
    zoomControl: false,
    attributionControl: false,
    crs: L.CRS.Simple
});

L.imageOverlay(imageUrl, imageBounds).addTo(map);

L.control.zoom({
    position: 'bottomright'
}).addTo(map);

var onEachFeature = function (feature, layer) {
    if (feature.properties && feature.properties.popupContent) {
        layer.bindPopup(feature.properties.popupContent, {closeButton: false});
    }
}

var geojsonFeature = {
    "type": "Feature",
    "properties": {
        "name": "test",
        "amenity": "test",
        "popupContent": "test"
    },
    "geometry": {
        "type": "Point",
        "coordinates": [866,1181]
    }
};

L.geoJSON(geojsonFeature, {
    onEachFeature: onEachFeature
}).addTo(map);

if (window.innerWidth <= 800) {
    map.setView([873, 853], -1);
} else {
    map.setView([1132, 898], 0);
}

map.on('click', function(e) {
    var coord = e.latlng;
    var lat = coord.lat;
    var lng = coord.lng;
    console.log("You clicked the map at latitude: " + lat + " and longitude: " + lng);
});

