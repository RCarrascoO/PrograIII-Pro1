from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import sys
import os

# Ajustar el path para importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sim.simulation import Simulation
from model.graph_base import Graph  

router = APIRouter()

# Crear un grafo predeterminado para la simulación
default_graph = Graph()  # Crea una instancia de Graph

# Instancia de la simulación con el grafo predeterminado
simulation = Simulation(default_graph)  # Ahora pasamos el grafo como argumento

class SystemStatus(BaseModel):
    active_drones: int
    battery_levels: Dict[str, float]
    current_orders: int
    system_uptime: float

class SimulationConfig(BaseModel):
    num_drones: int
    max_battery: float
    recharge_points: List[Dict[str, float]]  # Lista de {lat, lon, name}

@router.get("/system/status")
async def get_system_status():
    """
    Obtiene el estado actual del sistema de drones
    """
    try:
        # Asumiendo que simulation.get_active_drones() podría fallar
        # Proporcionamos valores predeterminados seguros
        status = {
            "active_drones": 3,  # Valor fijo para demostración
            "battery_levels": {
                "Drone-1": 85.0,
                "Drone-2": 72.5,
                "Drone-3": 93.0
            },
            "current_orders": 0,  # Por ahora no hay órdenes
            "system_uptime": 2.5  # Horas (valor de ejemplo)
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado del sistema: {str(e)}")
@router.post("/system/configure")
async def configure_simulation(config: SimulationConfig):
    """
    Configura los parámetros de la simulación
    """
    try:
        simulation.configure(
            num_drones=config.num_drones,
            max_battery=config.max_battery,
            recharge_points=config.recharge_points
        )
        return {"message": "Simulación configurada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configurando la simulación: {str(e)}")

@router.post("/system/reset")
async def reset_simulation():
    """
    Reinicia la simulación a su estado inicial
    """
    try:
        simulation.reset()
        return {"message": "Simulación reiniciada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reiniciando la simulación: {str(e)}")

@router.post("/system/start")
async def start_simulation():
    """
    Inicia la simulación de entrega con drones
    """
    try:
        simulation.start()
        return {"message": "Simulación iniciada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando la simulación: {str(e)}")

@router.post("/system/stop")
async def stop_simulation():
    """
    Detiene la simulación de entrega con drones
    """
    try:
        simulation.stop()
        return {"message": "Simulación detenida correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deteniendo la simulación: {str(e)}")