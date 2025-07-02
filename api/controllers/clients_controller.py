from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from pydantic import BaseModel
import sys
import os

# Ajustar el path para importar desde el directorio raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from domain.client import Client
from tda.hash_map import Map  # Ahora Map es un alias de HashMap

router = APIRouter()

# Modelos Pydantic para la API
class ClientBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    latitude: float
    longitude: float

class ClientCreate(ClientBase):
    pass

class ClientResponse(ClientBase):
    id: int
    
    class Config:
        orm_mode = True

# Simulación de almacenamiento (en producción usaríamos una BD)
clients_map = Map()  # Usando el alias Map de HashMap

@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate):
    # Asignar ID único y crear instancia de Client
    client_id = len(clients_map) + 1  # Usando el método __len__ de HashMap
    new_client = Client(
        client_id,
        client.name,
        client.email,
        client.phone,
        client.address,
        client.latitude,
        client.longitude
    )
    
    # Guardar en el Map
    clients_map.put(client_id, new_client)
    
    # Crear respuesta
    response = ClientResponse(
        id=client_id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        address=client.address,
        latitude=client.latitude,
        longitude=client.longitude
    )
    
    return response

@router.get("/clients", response_model=List[ClientResponse])
async def get_all_clients():
    # Obtener todos los clientes del HashMap
    clients = []
    for bucket in clients_map.buckets:
        for key, client in bucket:
            clients.append(ClientResponse(
                id=client.id,
                name=client.name,
                email=client.email,
                phone=client.phone,
                address=client.address,
                latitude=client.latitude,
                longitude=client.longitude
            ))
    return clients

@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int):
    client = clients_map.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
    return ClientResponse(
        id=client.id,
        name=client.name,
        email=client.email,
        phone=client.phone,
        address=client.address,
        latitude=client.latitude,
        longitude=client.longitude
    )

@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client_update: ClientBase):
    existing_client = clients_map.get(client_id)
    if not existing_client:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Actualizar campos
    existing_client.name = client_update.name
    existing_client.email = client_update.email
    existing_client.phone = client_update.phone
    existing_client.address = client_update.address
    existing_client.latitude = client_update.latitude
    existing_client.longitude = client_update.longitude
    
    # Actualizar en el Map
    clients_map.put(client_id, existing_client)
    
    return ClientResponse(
        id=existing_client.id,
        name=existing_client.name,
        email=existing_client.email,
        phone=existing_client.phone,
        address=existing_client.address,
        latitude=existing_client.latitude,
        longitude=existing_client.longitude
    )

@router.delete("/clients/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int):
    if clients_map.get(client_id) is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Necesitamos implementar remove() en HashMap
    # Como no existe en la clase HashMap actual, lo simulamos
    h = clients_map._hash(client_id)
    bucket = clients_map.buckets[h]
    for i, (k, v) in enumerate(bucket):
        if k == client_id:
            del bucket[i]
            return None
    
    raise HTTPException(status_code=404, detail="Cliente no encontrado")