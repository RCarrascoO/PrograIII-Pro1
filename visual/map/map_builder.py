import folium
import streamlit as st
from streamlit_folium import st_folium
import random
import numpy as np
from typing import Dict, List, Tuple, Optional

class MapBuilder:
    """Constructor de mapas interactivos para visualización de rutas y nodos"""
    
    def __init__(self, center_lat=-38.7359, center_lon=-72.5904):
        """
        Inicializa el constructor de mapas
        
        Args:
            center_lat: Latitud del centro (Temuco por defecto)
            center_lon: Longitud del centro (Temuco por defecto)
        """
        self.center = [center_lat, center_lon]
        self.bounds = {
            'north': center_lat + 0.05,
            'south': center_lat - 0.05,
            'east': center_lon + 0.05,
            'west': center_lon - 0.05
        }
        
        # Configuración de colores y estilos
        self.node_colors = {
            'warehouse': '#ff6b6b',
            'client': '#00FF00', 
            'recharge': '#45b7d1',
            'default': '#95a5a6'
        }
        
        self.node_icons = {
            'warehouse': 'home',
            'client': 'user',
            'recharge': 'bolt',
            'default': 'circle'
        }
    
    def create_base_map(self, zoom_start=13) -> folium.Map:
        """
        Crea un mapa base con configuración estándar
        
        Args:
            zoom_start: Nivel de zoom inicial
            
        Returns:
            Objeto folium.Map
        """
        m = folium.Map(
            location=self.center,
            zoom_start=zoom_start,
            tiles='OpenStreetMap'
        )
        
        # Agregar capa satelital
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Satellite View',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Agregar capa de terreno
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
            attr='Esri',
            name='Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Control de capas
        folium.LayerControl().add_to(m)
        
        return m
    
    def generate_node_coordinates(self, graph) -> Dict:
        """
        Genera coordenadas aleatorias para los nodos del grafo
        
        Args:
            graph: Grafo con nodos
            
        Returns:
            Diccionario {nodo: (lat, lon)}
        """
        coordinates = {}
        
        for node in graph.vertices():
            node_type = graph.get_node_type(node)
            
            if node_type == 'warehouse':
                # Warehouses más cerca del centro
                lat = random.uniform(
                    self.center[0] - 0.02,
                    self.center[0] + 0.02
                )
                lon = random.uniform(
                    self.center[1] - 0.02,
                    self.center[1] + 0.02
                )
            elif node_type == 'recharge':
                # Estaciones de recarga distribuidas
                lat = random.uniform(
                    self.center[0] - 0.035,
                    self.center[0] + 0.035
                )
                lon = random.uniform(
                    self.center[1] - 0.035,
                    self.center[1] + 0.035
                )
            else:  # client
                # Clientes en todo el rango
                lat = random.uniform(self.bounds['south'], self.bounds['north'])
                lon = random.uniform(self.bounds['west'], self.bounds['east'])
            
            coordinates[node] = (lat, lon)
        
        return coordinates
    
    def add_nodes_to_map(self, map_obj: folium.Map, graph, coordinates: Dict):
        """
        Agrega nodos del grafo al mapa
        
        Args:
            map_obj: Mapa de folium
            graph: Grafo con nodos
            coordinates: Diccionario de coordenadas
        """
        for node in graph.vertices():
            if node in coordinates:
                lat, lon = coordinates[node]
                node_type = graph.get_node_type(node)
                
                color = self.node_colors.get(node_type, self.node_colors['default'])
                icon = self.node_icons.get(node_type, self.node_icons['default'])
                
                # Crear popup con información
                popup_html = f"""
                <div style="width: 150px;">
                    <b>{node}</b><br>
                    <i>Type:</i> {node_type}<br>
                    <i>Coordinates:</i><br>
                    {lat:.6f}, {lon:.6f}
                </div>
                """
                
                # Marcador circular
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=f"{node} ({node_type})",
                    color='white',
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.8,
                    weight=2
                ).add_to(map_obj)
    
    def add_edges_to_map(self, map_obj: folium.Map, graph, coordinates: Dict, 
                        highlight_edges: Optional[set] = None):
        """
        Agrega aristas del grafo al mapa
        
        Args:
            map_obj: Mapa de folium
            graph: Grafo con aristas
            coordinates: Diccionario de coordenadas
            highlight_edges: Set de aristas a resaltar
        """
        if highlight_edges is None:
            highlight_edges = set()
        
        for edge in graph.edges():
            origin, destination = edge.endpoints()
            
            if origin in coordinates and destination in coordinates:
                origin_coords = coordinates[origin]
                dest_coords = coordinates[destination]
                
                # Verificar si la arista debe ser resaltada
                is_highlighted = (
                    (origin, destination) in highlight_edges or 
                    (destination, origin) in highlight_edges
                )
                
                folium.PolyLine(
                    locations=[origin_coords, dest_coords],
                    color='red' if is_highlighted else 'blue',
                    weight=4 if is_highlighted else 2,
                    opacity=0.8 if is_highlighted else 0.5,
                    popup=f"Edge: {origin} → {destination}<br>Cost: {edge.element()}"
                ).add_to(map_obj)
    
    def add_route_to_map(self, map_obj: folium.Map, route_path: List, 
                        coordinates: Dict, color='red', weight=4):
        """
        Agrega una ruta específica al mapa
        
        Args:
            map_obj: Mapa de folium
            route_path: Lista de nodos de la ruta
            coordinates: Diccionario de coordenadas
            color: Color de la línea
            weight: Grosor de la línea
        """
        if len(route_path) < 2:
            return
        
        # Crear coordenadas de la ruta
        route_coords = []
        for node in route_path:
            if node in coordinates:
                route_coords.append(coordinates[node])
        
        if len(route_coords) >= 2:
            # Línea principal de la ruta
            folium.PolyLine(
                locations=route_coords,
                color=color,
                weight=weight,
                opacity=0.8,
                popup=f"Route: {' → '.join(map(str, route_path))}"
            ).add_to(map_obj)
            
            # Marcador de inicio
            folium.Marker(
                location=route_coords[0],
                icon=folium.Icon(color='green', icon='play'),
                popup="<b>Start</b>",
                tooltip="Route Start"
            ).add_to(map_obj)
            
            # Marcador de fin
            folium.Marker(
                location=route_coords[-1],
                icon=folium.Icon(color='red', icon='stop'),
                popup="<b>End</b>",
                tooltip="Route End"
            ).add_to(map_obj)
            
            # Marcadores numerados para cada parada
            for i, (coord, node) in enumerate(zip(route_coords, route_path)):
                folium.Marker(
                    location=coord,
                    icon=folium.DivIcon(
                        html=f'<div style="background-color: orange; color: white; '
                             f'border-radius: 50%; width: 20px; height: 20px; '
                             f'text-align: center; line-height: 20px; font-weight: bold;">'
                             f'{i+1}</div>',
                        icon_size=(20, 20),
                        icon_anchor=(10, 10)
                    ),
                    popup=f"Stop {i+1}: {node}",
                    tooltip=f"Stop {i+1}"
                ).add_to(map_obj)
    
    def create_full_map(self, graph, highlight_route: Optional[List] = None, 
                       coordinates: Optional[Dict] = None) -> Tuple[folium.Map, Dict]:
        """
        Crea un mapa completo con nodos, aristas y opcionalmente una ruta resaltada
        
        Args:
            graph: Grafo a visualizar
            highlight_route: Lista de nodos de la ruta a resaltar
            coordinates: Coordenadas existentes (opcional)
            
        Returns:
            Tuple (mapa, coordenadas)
        """
        # Crear mapa base
        m = self.create_base_map()
        
        # Generar o usar coordenadas
        if coordinates is None:
            coordinates = self.generate_node_coordinates(graph)
        
        # Agregar nodos
        self.add_nodes_to_map(m, graph, coordinates)
        
        # Preparar aristas resaltadas
        highlight_edges = set()
        if highlight_route and len(highlight_route) > 1:
            for i in range(len(highlight_route) - 1):
                highlight_edges.add((highlight_route[i], highlight_route[i + 1]))
        
        # Agregar aristas
        self.add_edges_to_map(m, graph, coordinates, highlight_edges)
        
        # Agregar ruta específica
        if highlight_route:
            self.add_route_to_map(m, highlight_route, coordinates)
        
        # Agregar leyenda
        self.add_legend(m)
        
        return m, coordinates
    
    def add_legend(self, map_obj: folium.Map):
        """
        Agrega una leyenda al mapa
        
        Args:
            map_obj: Mapa de folium
        """
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 180px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px; border-radius: 5px;">
        <p style="margin: 0; font-weight: bold;">Node Types</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:#ff6b6b"></i> Warehouse</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:#00FF00"></i> Client</p>
        <p style="margin: 5px 0;"><i class="fa fa-circle" style="color:#45b7d1"></i> Recharge Station</p>
        <p style="margin: 5px 0;"><i class="fa fa-play" style="color:green"></i> Route Start</p>
        <p style="margin: 5px 0;"><i class="fa fa-stop" style="color:red"></i> Route End</p>
        </div>
        '''
        map_obj.get_root().html.add_child(folium.Element(legend_html))
    
    def display_map(self, map_obj: folium.Map, key: str = "map", 
                   width: int = 700, height: int = 500):
        """
        Muestra el mapa usando streamlit_folium
        
        Args:
            map_obj: Mapa de folium
            key: Clave única para el widget
            width: Ancho en píxeles
            height: Alto en píxeles
            
        Returns:
            Datos del mapa interactivo
        """
        return st_folium(
            map_obj,
            key=key,
            width=width,
            height=height,
            returned_objects=["last_object_clicked", "last_clicked"]
        )
    
    def create_heatmap(self, graph, visit_data: Optional[List] = None) -> folium.Map:
        """
        Crea un mapa de calor basado en visitas a nodos
        
        Args:
            graph: Grafo con nodos
            visit_data: Lista de tuplas (node, visits)
            
        Returns:
            Mapa de calor
        """
        try:
            from folium.plugins import HeatMap
        except ImportError:
            st.error("HeatMap plugin not available. Install with: pip install folium[plugins]")
            return self.create_base_map()
        
        m = self.create_base_map()
        
        if visit_data:
            coordinates = self.generate_node_coordinates(graph)
            heat_data = []
            
            for node, visits in visit_data:
                if node in coordinates:
                    lat, lon = coordinates[node]
                    heat_data.append([lat, lon, visits])
            
            if heat_data:
                HeatMap(heat_data).add_to(m)
        
        return m