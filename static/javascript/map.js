var map = L.map('map', {
    center: [51.505, -0.09],
    zoom: 13,
    zoomControl: false
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

L.control.zoom({
    position: 'topright'
}).addTo(map);
