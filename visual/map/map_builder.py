import folium
import os
import tempfile
import datetime

class MapBuilder:
    """
    Clase para crear mapas interactivos para el sistema de drones
    """
    
    def __init__(self, center=(38.7359, -72.5904), zoom_start=13):  # Coordenadas de Temuco
        """
        Inicializa un nuevo constructor de mapas
        
        Args:
            center: Coordenadas (lat, lon) del centro del mapa
            zoom_start: Nivel inicial de zoom
        """
        self.map = folium.Map(location=center, zoom_start=zoom_start)
        self.charging_stations = []
        self.drone_bases = []
        self.routes = []
    
    def add_charging_stations(self, stations):
        """
        Añade estaciones de carga al mapa
        
        Args:
            stations: Lista de diccionarios con lat, lon y name
        """
        for station in stations:
            folium.Marker(
                location=[station["lat"], station["lon"]],
                popup=folium.Popup(f"<b>{station['name']}</b><br>Estación de Carga", max_width=300),
                tooltip=station["name"],
                icon=folium.Icon(color="green", icon="plug", prefix='fa')
            ).add_to(self.map)
            self.charging_stations.append(station)
    
    def add_drone_base(self, lat, lon, name):
        """
        Añade una base de drones al mapa
        
        Args:
            lat: Latitud
            lon: Longitud
            name: Nombre de la base
        """
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(f"<b>{name}</b><br>Base de Drones", max_width=300),
            tooltip=name,
            icon=folium.Icon(color="red", icon="home", prefix='fa')
        ).add_to(self.map)
        self.drone_bases.append({"lat": lat, "lon": lon, "name": name})
    
    def add_node(self, lat, lon, name, node_type="client", popup_content=None):
        """
        Añade un nodo al mapa (cliente o almacén)
        
        Args:
            lat: Latitud
            lon: Longitud
            name: Nombre del nodo
            node_type: "client" o "storage"
            popup_content: Contenido adicional para el popup
        """
        icon_color = "blue" if node_type == "client" else "red"
        icon = "user" if node_type == "client" else "industry"
        
        if not popup_content:
            popup_content = f"<b>{name}</b><br>Tipo: {node_type}"
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=name,
            icon=folium.Icon(color=icon_color, icon=icon, prefix='fa')
        ).add_to(self.map)
    
    def add_route(self, origin, destination, max_battery=100.0, weight=1.0, color="blue", popup=None):
        """
        Añade una ruta al mapa
        
        Args:
            origin: Tupla (lat, lon) de origen
            destination: Tupla (lat, lon) de destino
            max_battery: Capacidad máxima de batería
            weight: Peso del envío
            color: Color de la línea
            popup: Contenido del popup
        """
        if not popup:
            popup = f"Peso: {weight} kg"
        
        # Añadir línea de ruta
        folium.PolyLine(
            locations=[origin, destination],
            color=color,
            weight=3,
            opacity=0.8,
            tooltip=popup
        ).add_to(self.map)
        
        # Añadir icono de drone en el punto medio
        mid_point = [(origin[0] + destination[0])/2, (origin[1] + destination[1])/2]
        folium.Marker(
            location=mid_point,
            icon=folium.Icon(color="purple", icon="plane", prefix='fa')
        ).add_to(self.map)
        
        # Guardar información de la ruta
        self.routes.append({
            "origin": origin,
            "destination": destination,
            "max_battery": max_battery,
            "weight": weight
        })
    
    def add_mst(self, mst_edges, node_coords):
        """
        Añade el árbol de expansión mínima al mapa
        
        Args:
            mst_edges: Lista de tuplas (u, v, weight) que representan el MST
            node_coords: Diccionario que mapea nodos a coordenadas (lat, lon)
        """
        for u, v, weight in mst_edges:
            folium.PolyLine(
                locations=[node_coords[u], node_coords[v]],
                color='green',
                weight=3,
                opacity=0.8,
                tooltip=f"Peso: {weight:.2f}"
            ).add_to(self.map)
    
    def add_path_route(self, path_coords, color='red', weight=4, tooltip="Ruta óptima"):
        """
        Añade una ruta calculada por un algoritmo de camino más corto
        
        Args:
            path_coords: Lista de coordenadas [(lat, lon), ...] que forman la ruta
            color: Color de la línea
            weight: Grosor de la línea
            tooltip: Texto del tooltip
        """
        folium.PolyLine(
            locations=path_coords,
            color=color,
            weight=weight,
            opacity=0.8,
            tooltip=tooltip
        ).add_to(self.map)
    
    def save_map(self, filename=None):
        """
        Guarda el mapa en un archivo HTML
        
        Args:
            filename: Nombre del archivo (si es None, se genera un nombre temporal)
            
        Returns:
            Ruta del archivo guardado
        """
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"drone_map_{timestamp}.html"
        
        # Asegurarse de que la carpeta existe
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else ".", exist_ok=True)
        
        # Guardar mapa
        self.map.save(filename)
        return filename