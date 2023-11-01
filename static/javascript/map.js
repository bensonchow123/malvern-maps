var imageUrl = '/static/images/map.png';

// Define the bounds of your image
var imageBounds= [[0, 0], [1567, 1653]]; // Replace with the actual size of your image

// Remove the tileLayer and add an imageOverlay
var map = L.map('map', {
    center: [0, 0],
    zoom: 0,
    minZoom: -5,
    zoomControl: false,
    crs: L.CRS.Simple
});

L.imageOverlay(imageUrl, imageBounds).addTo(map);

L.control.zoom({
    position: 'topright'
}).addTo(map);

// Set the view to the center of your image
map.setView([imageBounds[1][1] / 2, imageBounds[1][0] / 2]);