var imageUrl = '/static/images/map.png';

var imageBounds= [[0, 0], [1567, 1653]];

var map = L.map('map', {
    center: [890, 881],
    zoom: 0,
    minZoom: -1,
    zoomControl: false,
    attributionControl: false,
    crs: L.CRS.Simple
});

L.imageOverlay(imageUrl, imageBounds).addTo(map);

L.control.zoom({
    position: 'topright'
}).addTo(map);

map.setView([imageBounds[1][1] / 2, imageBounds[1][0] / 2]);
map.on('click', function(e) {
    var coord = e.latlng;
    var lat = coord.lat;
    var lng = coord.lng;
    console.log("You clicked the map at latitude: " + lat + " and longitude: " + lng);
});
