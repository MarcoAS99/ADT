class Map(object):
    def __init__(self):
        self._points = []
        self._taxis = []

    def add_point(self, coordinates):
        self._points.append(coordinates)

    def add_taxi(self, taxi):
        self._taxis.append(
            (taxi['estado'], taxi['ubicacion'], taxi['destino']))

    def add_taxis(self, taxis_coords, taxis):
        for taxi in taxis:
            self.add_taxi(taxi)
        for coords in taxis_coords.values():
            self.add_point(coords)

    def get_script(self):
        centerLat = sum((x[0] for x in self._points)) / len(self._points)
        centerLon = sum((x[1] for x in self._points)) / len(self._points)
        markersCode = "\n".join(
            ["""marker = L.marker([{lat}, {lon}], {{icon: myIcon}}).addTo(mymap);
                marker.bindPopup('<ul class="list-group list-group-flush"><li class="list-group-item">Estado: {estado}</li><li class="list-group-item">Ubicacion: {ubi}</li><li class="list-group-item">Destino: {dest}</li></ul>');"""
             .format(lat=x[0], lon=x[1], estado=self._taxis[i][0], ubi=self._taxis[i][1], dest=self._taxis[i][2]) for i, x in enumerate(self._points)
             ])
        return """
                var marker;
                mymap = L.map('mimapa').setView([{centerLat},{centerLon}], 10.25);
                var myIcon = L.icon({{
                    iconUrl: '/static/img/icon_taxi.png',
                    iconSize: [38, 38],
                    iconAnchor: [22, 94],
                    popupAnchor: [-3, -76]
                }});
                {markersCode}
                L.tileLayer('https://api.mapbox.com/styles/v1/{{id}}/tiles/{{z}}/{{x}}/{{y}}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw', {{
                    maxZoom: 25,
                    attribution: 'Datos del mapa de &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a>, ' + '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' + 'Imágenes © <a href="https://www.mapbox.com/">Mapbox</a>',
                    id: 'mapbox/streets-v11'
                }}).addTo(mymap);
        """.format(centerLat=centerLat, centerLon=centerLon,
                   markersCode=markersCode)
