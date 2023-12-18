var imageUrl = '/static/images/map.png';
var imageBounds = [[0, 0], [1951, 1579]];

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

const redIcon = new L.Icon({
    iconUrl:
        "./static/images/leaflet-icon-red.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [20, 32.8],
    iconAnchor: [9.6, 32.8],
    popupAnchor: [0.8, -27.2],
    shadowSize: [32.8, 32.8]
});

const greenIcon = new L.Icon({
    iconUrl:
        "./static/images/leaflet-icon-green.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [20, 32.8],
    iconAnchor: [9.6, 32.8],
    popupAnchor: [0.8, -27.2],
    shadowSize: [32.8, 32.8]
});

const yellowIcon = new L.Icon({
    iconUrl:
        "./static/images/leaflet-icon-yellow.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [15, 24.6],
    iconAnchor: [7.2, 24.6],
    popupAnchor: [0.6, -20.4],
    shadowSize: [24.6, 24.6]
});
const greyIcon = new L.Icon({
    iconUrl:
        "./static/images/leaflet-icon-grey.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [15, 24.6],
    iconAnchor: [7.2, 24.6],
    popupAnchor: [0.6, -20.4],
    shadowSize: [24.6, 24.6]
});
const blueIcon = new L.Icon({
    iconUrl:
        "./static/images/leaflet-icon-blue.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
    iconSize: [20, 32.8],
    iconAnchor: [9.6, 32.8],
    popupAnchor: [0.8, -27.2],
    shadowSize: [32.8, 32.8]
});

fetch('/static/json/nodes.json')
    .then((response) => response.json())
    .then((nodesDb) => {
        if (shortestPathCalculationResults) { // render only the shortest path
            shortestPathCalculationResults.forEach((node, index) => {
            let coordinates = nodesDb[node].cords_on_map;
            let marker;
            if (index === 0) {
                // starting point - green icon
                marker = L.marker(coordinates, {icon: greenIcon});
            } else if (index === shortestPathCalculationResults.length - 1) {
                // destination - red icon
                marker = L.marker(coordinates, {icon: redIcon});
            } else {
                // All other points - Yellow icon
                marker = L.marker(coordinates, {icon: yellowIcon});
            }
            marker.bindPopup('<div class="text-center">' + node + '</div>').openPopup();
            marker.addTo(map);
            });
        }
        else { // render every node
            for (let key in nodesDb) {
                let node = nodesDb[key];
                let coordinates = node.cords_on_map;
                if (coordinates.length > 0) {
                    let icon;
                    switch(node.starting_icon_colour) {
                        case 'grey':
                            icon = greyIcon;
                            break;
                        case "blue":
                            icon = blueIcon;
                            break;
                    }
                    let marker = L.marker(coordinates, {icon: icon});
                    marker.bindPopup('<div class="text-center">' + key + '</div>');
                    marker.addTo(map);
                }
            }
        }
    });

if (window.innerWidth <= 800) {
    map.setView([1072, 819], -1);
} else {
    map.setView([1510, 841], 0);
}


