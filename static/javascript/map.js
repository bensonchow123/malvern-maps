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
    position: 'bottomright'
}).addTo(map);

map.setView([imageBounds[1][1] / 2, imageBounds[1][0] / 2]);
setTimeout(function() {
    map.invalidateSize();
}, 2000);