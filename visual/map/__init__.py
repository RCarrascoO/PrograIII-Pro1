"""
Módulo de visualización geográfica en mapa
Contiene funcionalidades para:
- Construcción de mapas base con rutas y nodos
- Cálculo y resumen de trayectos de vuelo
"""

from .map_builder import MapBuilder
from .flight_summary import FlightSummary

__all__ = [
    'MapBuilder',
    'FlightSummary'
]