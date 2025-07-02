from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import sys
import os

# Ajustar el path para importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domain.order import Order
from tda.AVL_base import AVL  # Ajustado para usar AVL_base.py en lugar de avl.py
from tda.hash_map import Map  # Ahora Map es un alias de HashMap

router = APIRouter()

# Modelos Pydantic para la API
class OrderBase(BaseModel):
    client_id: int
    origin: str
    destination: str
    weight: float
    priority: int
    description: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: int
    status: str
    creation_date: datetime
    estimated_delivery_time: Optional[float] = None
    battery_usage: Optional[float] = None
    distance: Optional[float] = None
    
    class Config:
        orm_mode = True

# Simulación de almacenamiento (en producción usaríamos una BD)
orders_map = Map()  # Usando el alias Map de HashMap
frequent_routes = AVL()

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate):
    # Asignar ID único y crear instancia de Order
    order_id = len(orders_map) + 1  # Usando el método __len__ de HashMap
    new_order = Order(
        order_id, 
        order.client_id,
        order.origin,
        order.destination,
        order.weight,
        order.priority,
        order.description
    )
    
    # Guardar en el Map
    orders_map.put(order_id, new_order)
    
    # Registrar la ruta en el AVL de rutas frecuentes
    route_key = f"{order.origin}-{order.destination}"
    if frequent_routes.search(route_key) is not None:
        route_node = frequent_routes.search(route_key)
        route_node.data["count"] += 1
    else:
        frequent_routes.insert(route_key, {"count": 1, "origin": order.origin, "destination": order.destination})
    
    # Crear respuesta
    response = OrderResponse(
        id=order_id,
        client_id=order.client_id,
        origin=order.origin,
        destination=order.destination,
        weight=order.weight,
        priority=order.priority,
        description=order.description,
        status="PENDING",
        creation_date=datetime.now(),
        estimated_delivery_time=None,  # Se calculará después
        battery_usage=None,  # Se calculará después
        distance=None  # Se calculará después
    )
    
    return response

@router.get("/orders", response_model=List[OrderResponse])
async def get_all_orders():
    # Obtener todas las órdenes del HashMap
    # Nota: Ajustamos para usar la forma en que HashMap almacena los datos
    orders = []
    for bucket in orders_map.buckets:
        for key, order in bucket:
            orders.append(OrderResponse(
                id=order.id,
                client_id=order.client_id,
                origin=order.origin,
                destination=order.destination,
                weight=order.weight,
                priority=order.priority,
                description=order.description,
                status=order.status,
                creation_date=order.creation_date,
                estimated_delivery_time=order.estimated_delivery_time,
                battery_usage=order.battery_usage,
                distance=order.distance
            ))
    return orders

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    order = orders_map.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    return OrderResponse(
        id=order.id,
        client_id=order.client_id,
        origin=order.origin,
        destination=order.destination,
        weight=order.weight,
        priority=order.priority,
        description=order.description,
        status=order.status,
        creation_date=order.creation_date,
        estimated_delivery_time=order.estimated_delivery_time,
        battery_usage=order.battery_usage,
        distance=order.distance
    )

@router.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order_update: OrderBase):
    existing_order = orders_map.get(order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Actualizar campos
    existing_order.client_id = order_update.client_id
    existing_order.origin = order_update.origin
    existing_order.destination = order_update.destination
    existing_order.weight = order_update.weight
    existing_order.priority = order_update.priority
    existing_order.description = order_update.description
    
    # Actualizar en el Map
    orders_map.put(order_id, existing_order)
    
    return OrderResponse(
        id=existing_order.id,
        client_id=existing_order.client_id,
        origin=existing_order.origin,
        destination=existing_order.destination,
        weight=existing_order.weight,
        priority=existing_order.priority,
        description=existing_order.description,
        status=existing_order.status,
        creation_date=existing_order.creation_date,
        estimated_delivery_time=existing_order.estimated_delivery_time,
        battery_usage=existing_order.battery_usage,
        distance=existing_order.distance
    )

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int):
    if orders_map.get(order_id) is None:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Necesitamos implementar remove() en HashMap
    # Como no existe en la clase HashMap actual, lo simulamos
    h = orders_map._hash(order_id)
    bucket = orders_map.buckets[h]
    for i, (k, v) in enumerate(bucket):
        if k == order_id:
            del bucket[i]
            return None
    
    raise HTTPException(status_code=404, detail="Pedido no encontrado")