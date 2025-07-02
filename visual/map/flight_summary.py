import math
from typing import Dict

def calculate_flight_summary(
    origin_lat: float,
    origin_lon: float,
    destination_lat: float,
    destination_lon: float,
    package_weight: float,
    max_battery: float = 100.0
) -> Dict[str, float]:
    """
    Calcula la distancia, tiempo estimado y uso de batería para un vuelo entre dos puntos
    
    Args:
        origin_lat: Latitud del origen
        origin_lon: Longitud del origen
        destination_lat: Latitud del destino
        destination_lon: Longitud del destino
        package_weight: Peso del paquete en kg
        max_battery: Capacidad máxima de la batería
    
    Returns:
        Diccionario con distancia (km), tiempo estimado (min) y uso de batería (%)
    """
    # Calcular distancia usando la fórmula haversine
    distance = calculate_distance(origin_lat, origin_lon, destination_lat, destination_lon)
    
    # Constantes para el modelo
    BASE_SPEED = 30.0  # km/h
    WEIGHT_FACTOR = 0.1  # Reducción de velocidad por kg
    BATTERY_PER_KM = 5.0  # % de batería por km
    BATTERY_PER_KG_KM = 0.5  # % adicional de batería por kg por km
    
    # Calcular velocidad ajustada por peso
    adjusted_speed = BASE_SPEED - (package_weight * WEIGHT_FACTOR)
    adjusted_speed = max(15.0, adjusted_speed)  # Mínimo 15 km/h
    
    # Calcular tiempo estimado en minutos
    estimated_time = (distance / adjusted_speed) * 60
    
    # Calcular uso de batería
    battery_usage = (BATTERY_PER_KM * distance) + (BATTERY_PER_KG_KM * package_weight * distance)
    
    # Normalizar el uso de batería al valor máximo
    normalized_battery_usage = (battery_usage / max_battery) * 100
    
    return {
        "distance": distance,
        "estimated_time": estimated_time,
        "battery_usage": normalized_battery_usage
    }

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia en km entre dos puntos usando la fórmula haversine
    
    Args:
        lat1: Latitud del primer punto
        lon1: Longitud del primer punto
        lat2: Latitud del segundo punto
        lon2: Longitud del segundo punto
    
    Returns:
        Distancia en kilómetros
    """
    # Radio de la Tierra en km
    R = 6371.0
    
    # Convertir a radianes
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferencias
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Fórmula haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance